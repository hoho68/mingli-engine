import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


_MANUAL_APPLICATION_FIXTURE_CANDIDATES = [
    {
        "candidate_id": "candidate_mingli_pattern_strength_017_001",
        "material_id": "material_mingli_true_formula_teacher_pdf",
        "source_locator": "learning-reference:note_mingli_true_formula_teacher_001#lp_mingli_pattern_strength_001; locator_requirement=page_or_section_required",
        "extracted_meaning": "Pattern strength material should stay conditional until source locator and chart context are reviewed.",
        "short_quote": "",
        "proposed_rule_family": "pattern_strength",
        "risk_tier": "sensitive",
        "status": "pending_review",
        "proposed_limitations": [
            "State uncertainty for timing and pattern interpretation.",
            "Include limitation language; do not guarantee outcome timing.",
        ],
        "related_evidence_ids": [],
        "related_conflict_ids": [],
        "related_gap_ids": [],
        "duplicate_of": "",
        "created_by": "learning_reference_curation",
        "created_at": "2026-06-01",
    },
    {
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "material_id": "material_duan_plain_mingxue_outline_pdf",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001; locator_requirement=page_or_section_required",
        "extracted_meaning": "Duan Plain Mingxue Outline can organize ten-god relationships and pattern-strength review as source-backed taxonomy.",
        "short_quote": "",
        "proposed_rule_family": "ten_god_relation",
        "risk_tier": "ordinary",
        "status": "pending_review",
        "proposed_limitations": [
            "Keep as structural taxonomy until locator and chart context are reviewed.",
        ],
        "related_evidence_ids": [],
        "related_conflict_ids": [],
        "related_gap_ids": [],
        "duplicate_of": "",
        "created_by": "learning_reference_curation",
        "created_at": "2026-06-01",
    },
    {
        "candidate_id": "candidate_mingxue_five_element_balance_017_001",
        "material_id": "material_mingxue_golden_voice_pdf",
        "source_locator": "learning-reference:note_mingxue_golden_voice_001#lp_mingxue_five_element_balance_001; locator_requirement=page_or_section_required",
        "extracted_meaning": "Mingxue Golden Voice can support five-element terminology only after narrower locator review.",
        "short_quote": "",
        "proposed_rule_family": "five_element_balance",
        "risk_tier": "ordinary",
        "status": "pending_review",
        "proposed_limitations": [
            "Keep as terminology taxonomy until locator and chart context are reviewed.",
        ],
        "related_evidence_ids": [],
        "related_conflict_ids": [],
        "related_gap_ids": [],
        "duplicate_of": "",
        "created_by": "learning_reference_curation",
        "created_at": "2026-06-01",
    },
    {
        "candidate_id": "candidate_hongfu_remedy_boundary_017_001",
        "material_id": "material_fortune_reading_hongfu_qitian_pdf",
        "source_locator": "learning-reference:note_fortune_reading_hongfu_qitian_001#lp_hongfu_remedy_boundary_001; locator_requirement=page_or_section_required",
        "extracted_meaning": "Hongfu Qitian remedy-boundary material should stay conditional until locator and safety context are reviewed.",
        "short_quote": "",
        "proposed_rule_family": "remedy_boundary",
        "risk_tier": "sensitive",
        "status": "pending_review",
        "proposed_limitations": [
            "State uncertainty for remedy-boundary interpretation.",
            "Include limitation language; avoid certainty about effects.",
        ],
        "related_evidence_ids": [],
        "related_conflict_ids": [],
        "related_gap_ids": [],
        "duplicate_of": "",
        "created_by": "learning_reference_curation",
        "created_at": "2026-06-01",
    },
]


def _write_json_fixture(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_manual_application_fixture(path):
    _write_json_fixture(
        path / "source_materials.json",
        [
            {
                "material_id": material_id,
                "title": title,
                "material_type": "pdf",
                "file_label": file_label,
                "tracking_status": "external_untracked",
                "preparation_status": "indexed",
            }
            for material_id, title, file_label in [
                ("material_mingli_true_formula_teacher_pdf", "Mingli True Formula Teacher", "mingli-true-formula-teacher.pdf"),
                ("material_duan_plain_mingxue_outline_pdf", "Duan Plain Mingxue Outline", "duan-plain-mingxue-outline.pdf"),
                ("material_mingxue_golden_voice_pdf", "Mingxue Golden Voice", "mingxue-golden-voice.pdf"),
                ("material_fortune_reading_hongfu_qitian_pdf", "Fortune Reading Hongfu Qitian", "fortune-reading-hongfu-qitian.pdf"),
            ]
        ],
    )
    _write_json_fixture(path / "candidate_extracts.json", _MANUAL_APPLICATION_FIXTURE_CANDIDATES)
    _write_json_fixture(path / "review_decisions.json", [])



REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"
MANIFEST_PATH = EXAMPLES_DIR / "report-regression-cases.json"

REQUIRED_FIELDS = {"id", "kind", "command", "input", "purpose"}
SUPPORTED_KINDS = {"safe_markdown", "high_risk_markdown", "safety_json"}
SUPPORTED_COMMANDS = {"calculate-report", "generate-report"}
SAFE_SOURCE_TYPES = {"auto_calculated", "external_verified"}
RAW_READER_LABELS = (
    "auto_calculated",
    "external_verified",
    "medium",
    "gregorian",
    "year：",
    "month：",
    "day：",
    "hour：",
)
ABSOLUTE_DESTINY_PHRASES = ("必定", "注定", "一定会", "死定")
LAYER_HEADINGS = (
    "## 快速导读",
    "## 第一层：基础资料",
    "## 第二层：结构观察",
    "## 第三层：解读边界",
    "## 第四层：行动反思",
)
EVIDENCE_NOTE_PHRASES = (
    "### 观察依据",
    "来源依据：",
    "四柱依据：",
    "五行依据：",
    "十神依据：",
    "行动依据：",
    "不预测具体结果",
)
EXPANDED_EVIDENCE_PHRASES = (
    "命理依据：",
    "来源摘要：",
    "正式判断：",
    "证据：",
    "盘面：",
    "分歧说明：",
)
EXPANDED_RULE_FAMILIES = (
    "pattern_strength",
    "five_element_balance",
    "useful_god_candidate",
    "taboo_god_candidate",
    "ten_god_relation",
    "branch_interaction",
    "blind_image_method",
    "luck_cycle",
    "remedy_boundary",
    "high_risk_signal",
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else os.pathsep.join([src_path, env["PYTHONPATH"]])
    )
    return subprocess.run(
        [sys.executable, "-m", "mingli_engine.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def _load_cases() -> list[dict[str, Any]]:
    assert MANIFEST_PATH.exists(), "Missing report regression manifest"
    cases = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    assert cases
    return cases


def _assert_in_order(text: str, headings: tuple[str, ...]) -> None:
    search_from = 0
    for heading in headings:
        position = text.find(heading, search_from)
        assert position != -1, heading
        search_from = position + len(heading)


def _safe_markdown_cases() -> list[dict[str, Any]]:
    cases = [
        case for case in _load_cases() if case.get("kind") == "safe_markdown"
    ]
    source_types = {case.get("source_type") for case in cases}
    assert "auto_calculated" in source_types
    assert "external_verified" in source_types
    return cases


def _safety_json_cases() -> list[dict[str, Any]]:
    cases = [case for case in _load_cases() if case.get("kind") == "safety_json"]
    assert cases
    return cases


def _high_risk_markdown_cases() -> list[dict[str, Any]]:
    cases = [
        case for case in _load_cases() if case.get("kind") == "high_risk_markdown"
    ]
    assert cases
    return cases


def _assert_safe_case_shape(case: dict[str, Any]) -> None:
    _assert_manifest_case_shape(case)
    assert case.get("kind") == "safe_markdown"


def _assert_high_risk_case_shape(case: dict[str, Any]) -> None:
    _assert_manifest_case_shape(case)
    assert case.get("kind") == "high_risk_markdown"


def _assert_safety_case_shape(case: dict[str, Any]) -> None:
    _assert_manifest_case_shape(case)
    assert case.get("kind") == "safety_json"


def _assert_manifest_case_shape(case: dict[str, Any]) -> None:
    assert REQUIRED_FIELDS.issubset(case), case
    assert case.get("id")
    assert case.get("kind") in SUPPORTED_KINDS
    assert case.get("command") in SUPPORTED_COMMANDS
    assert case.get("purpose")
    input_ref = case.get("input")
    assert isinstance(input_ref, str)
    assert (REPO_ROOT / input_ref).exists(), case
    if case["kind"] in {"safe_markdown", "high_risk_markdown"}:
        assert case.get("source_type") in SAFE_SOURCE_TYPES
    if case["kind"] == "safety_json":
        assert case.get("expected_category")


def _assert_safe_markdown(
    case: dict[str, Any], result: subprocess.CompletedProcess[str]
) -> None:
    assert result.returncode == 0, result.stderr
    markdown = result.stdout
    assert markdown.startswith("# 八字结构化报告")
    assert "## 免责声明" in markdown
    _assert_in_order(markdown, LAYER_HEADINGS)
    _assert_in_order(
        markdown,
        (
            "### 四柱与五行摘要",
            "### 十神摘要",
            "### 观察依据",
            "### 结构分析",
            "### 性格倾向",
        ),
    )
    for phrase in EVIDENCE_NOTE_PHRASES:
        assert phrase in markdown
    for phrase in EXPANDED_EVIDENCE_PHRASES:
        assert phrase in markdown
    for rule_family in EXPANDED_RULE_FAMILIES:
        assert rule_family in markdown
    assert "### 排盘来源与假设" in markdown.splitlines()
    assert "### 四柱与五行摘要" in markdown.splitlines()
    assert "### 行动建议" in markdown.splitlines()
    assert "公历" in markdown
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert f"- {pillar_name}：" in markdown
    assert "五行数量可以先作为结构观察材料来看" in markdown
    assert "十神关系可以先按四个柱位理解为结构线索" in markdown
    assert "基础结构可以先看分布是否集中" in markdown
    assert "先核对资料与假设" in markdown
    assert "结构观察提供的是线索，不是最终判断" in markdown
    assert "这些边界是为了防止过度断言" in markdown
    assert "行动反思只作为复盘提示" in markdown
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in markdown
    for phrase in ABSOLUTE_DESTINY_PHRASES:
        assert phrase not in markdown
    if case["source_type"] == "auto_calculated":
        assert "系统自动排盘" in markdown
        assert "中等可信度" in markdown
    if case["source_type"] == "external_verified":
        assert "外部排盘已核对" in markdown
        assert "来源类型：系统自动排盘" not in markdown


def _assert_safe_html(
    case: dict[str, Any], result: subprocess.CompletedProcess[str]
) -> None:
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    html = result.stdout
    assert html.startswith("<!doctype html>")
    assert '<html lang="zh-CN">' in html
    assert '<meta charset="utf-8">' in html
    assert "<title>" in html
    assert "<style>" in html
    assert html.count("<main") == 1
    assert html.rstrip().endswith("</html>")
    assert "# " not in html
    assert "<script" not in html.lower()
    assert "onclick=" not in html.lower()
    html_layer_headings = tuple(
        heading.removeprefix("## ") for heading in LAYER_HEADINGS
    )
    _assert_in_order(html, html_layer_headings)
    evidence_heading = EVIDENCE_NOTE_PHRASES[0].removeprefix("### ")
    structure_position = html.find(html_layer_headings[2])
    evidence_position = html.find(evidence_heading)
    boundary_position = html.find(html_layer_headings[3])
    assert structure_position < evidence_position < boundary_position
    for phrase in (evidence_heading, *EVIDENCE_NOTE_PHRASES[1:]):
        assert phrase in html
    for phrase in EXPANDED_EVIDENCE_PHRASES:
        assert phrase in html
    for rule_family in EXPANDED_RULE_FAMILIES:
        assert rule_family in html
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in html
    for phrase in ABSOLUTE_DESTINY_PHRASES:
        assert phrase not in html
    if case["source_type"] == "auto_calculated":
        assert "external_verified" not in html
    if case["source_type"] == "external_verified":
        assert "auto_calculated" not in html


def _assert_high_risk_markdown(
    case: dict[str, Any], result: subprocess.CompletedProcess[str]
) -> None:
    _assert_safe_markdown(case, result)
    markdown = result.stdout
    assert "高风险材料边界" in markdown
    assert "传统风险信号" in markdown
    assert "不输出精确结果" in markdown


def _assert_safety_json(
    case: dict[str, Any], result: subprocess.CompletedProcess[str]
) -> None:
    assert result.returncode == 3, result.stderr
    assert not result.stdout.startswith("# 八字结构化报告")
    assert "### 观察依据" not in result.stdout
    payload = json.loads(result.stdout)
    assert payload["allowed"] is False
    assert case["expected_category"] in payload["red_line_categories"]


def test_manifest_lists_safe_markdown_regression_cases():
    cases = _safe_markdown_cases()
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))
    for case in cases:
        _assert_safe_case_shape(case)


def test_manifest_lists_safety_json_regression_cases():
    for case in _safety_json_cases():
        _assert_safety_case_shape(case)


def test_manifest_lists_high_risk_markdown_regression_cases():
    for case in _high_risk_markdown_cases():
        _assert_high_risk_case_shape(case)


def test_report_regression_manifest_is_self_validating():
    cases = _load_cases()
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))
    for case in cases:
        _assert_manifest_case_shape(case)
    assert any(
        case["kind"] == "safe_markdown"
        and case.get("source_type") == "auto_calculated"
        for case in cases
    )
    assert any(
        case["kind"] == "safe_markdown"
        and case.get("source_type") == "external_verified"
        for case in cases
    )
    assert any(case["kind"] == "safety_json" for case in cases)
    assert any(case["kind"] == "high_risk_markdown" for case in cases)


def test_manifest_validation_rejects_invalid_case_shapes():
    valid_case = {
        "id": "safe-auto-gregorian",
        "kind": "safe_markdown",
        "command": "calculate-report",
        "input": "examples/birth-profile.auto-gregorian.json",
        "purpose": "Guards a valid safe Markdown case.",
        "source_type": "auto_calculated",
    }
    invalid_cases = (
        valid_case | {"id": ""},
        valid_case | {"kind": "unsupported"},
        valid_case | {"command": "new-command"},
        valid_case | {"input": "examples/missing-case.json"},
        valid_case | {"purpose": ""},
        valid_case | {"source_type": "raw"},
        {
            "id": "unsafe-lifespan-focus",
            "kind": "safety_json",
            "command": "calculate-report",
            "input": "examples/birth-profile.unsafe-focus.json",
            "purpose": "Guards safety JSON cases.",
        },
    )

    for case in invalid_cases:
        with pytest.raises(AssertionError):
            _assert_manifest_case_shape(case)


def test_safe_markdown_regression_cases_keep_report_contracts():
    for case in _safe_markdown_cases():
        result = _run_cli(
            case["command"],
            "--input",
            str(REPO_ROOT / case["input"]),
            "--format",
            "markdown",
        )
        _assert_safe_markdown(case, result)


def test_safe_regression_cases_keep_html_report_contracts():
    cases = _safe_markdown_cases()
    assert {case["source_type"] for case in cases} == SAFE_SOURCE_TYPES
    for case in cases:
        result = _run_cli(
            case["command"],
            "--input",
            str(REPO_ROOT / case["input"]),
            "--format",
            "html",
        )
        _assert_safe_html(case, result)


def test_high_risk_markdown_regression_cases_keep_narrowed_contracts():
    for case in _high_risk_markdown_cases():
        result = _run_cli(
            case["command"],
            "--input",
            str(REPO_ROOT / case["input"]),
            "--format",
            "markdown",
        )
        _assert_high_risk_markdown(case, result)


def test_pending_source_intake_candidates_are_not_formal_report_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import load_candidate_extracts

    candidates = load_candidate_extracts(tmp_path)
    pending_candidate_ids = {
        candidate.candidate_id
        for candidate in candidates
        if candidate.status == "pending_review"
    }
    formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    assert pending_candidate_ids
    assert pending_candidate_ids.isdisjoint(formal_evidence_ids)


def test_pending_candidate_review_worklist_does_not_change_formal_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        list_pending_candidate_review_worklist,
        load_candidate_extracts,
    )

    before_candidate_ids = {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    worklist = list_pending_candidate_review_worklist(tmp_path)

    assert {item.candidate_id for item in worklist} == {
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    }
    assert {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_decision_packets_do_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        list_pending_candidate_review_decision_packets,
        load_candidate_extracts,
        load_review_decisions,
    )

    before_candidate_ids = {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    packets = list_pending_candidate_review_decision_packets(tmp_path)

    assert {packet.candidate_id for packet in packets} == {
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    }
    assert {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_ids
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_packet_summary_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_packet_summary,
        load_candidate_extracts,
        load_review_decisions,
    )

    before_candidate_ids = {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    summary = build_pending_candidate_review_packet_summary(tmp_path)

    assert summary.packet_count == 4
    assert summary.review_decision_delta == 0
    assert summary.formal_evidence_delta == 0
    assert {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_ids
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_action_queue_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_action_queue,
        load_candidate_extracts,
        load_review_decisions,
    )

    before_candidate_ids = {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    queue = build_pending_candidate_review_action_queue(tmp_path)

    assert [item.candidate_id for item in queue] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_ids
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_action_markdown_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_action_queue_markdown,
    )

    before_candidate_ids = {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    markdown = render_pending_candidate_review_action_queue_markdown(tmp_path)

    assert markdown.startswith("# Pending Candidate Review Action Queue")
    assert {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_ids
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_input_templates_do_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        list_pending_candidate_review_input_templates,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_input_templates_markdown,
    )

    before_candidate_ids = {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    templates = list_pending_candidate_review_input_templates(tmp_path)
    markdown = render_pending_candidate_review_input_templates_markdown(tmp_path)

    assert [template.candidate_id for template in templates] == [
        "candidate_mingli_pattern_strength_017_001",
        "candidate_duan_ten_god_relation_017_001",
        "candidate_mingxue_five_element_balance_017_001",
        "candidate_hongfu_remedy_boundary_017_001",
    ]
    assert markdown.startswith("# Pending Candidate Review Input Templates")
    assert {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_ids
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_draft_validation_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_draft_validation_markdown,
        validate_pending_candidate_review_decision_draft,
    )

    before_candidate_ids = {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_hongfu_remedy_boundary_017_001",
        "candidate_id": "candidate_hongfu_remedy_boundary_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "source:hongfu-qitian#section-remedy-boundary",
        "source_page_or_section_locator": "source:hongfu-qitian#section-remedy-boundary",
        "source_quality": "review_note",
        "confidence": "moderate",
        "rationale": "Locator and conditional safety language are reviewable.",
        "approval_limitations": [
            "Use only as conditional traditional remedy-boundary context."
        ],
        "uncertainty_and_limitation_language": (
            "Frame as uncertain traditional context, not guaranteed effect."
        ),
        "required_changes": [],
        "rejection_reason": "",
    }

    result = validate_pending_candidate_review_decision_draft(draft, tmp_path)
    markdown = render_pending_candidate_review_draft_validation_markdown([draft], tmp_path)

    assert result.ready_for_manual_application is True
    assert markdown.startswith("# Pending Candidate Review Draft Validation")
    assert {
        candidate.candidate_id for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_ids
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_application_guard_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_application_guard,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_application_guard_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_hongfu_remedy_boundary_017_001",
        "candidate_id": "candidate_hongfu_remedy_boundary_017_001",
        "review_outcome": "approved",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "source:hongfu-qitian#section-remedy-boundary",
        "source_page_or_section_locator": "source:hongfu-qitian#section-remedy-boundary",
        "source_quality": "review_note",
        "confidence": "moderate",
        "rationale": "Locator and conditional safety language are reviewable.",
        "approval_limitations": [
            "Use only as conditional traditional remedy-boundary context."
        ],
        "uncertainty_and_limitation_language": (
            "Frame as uncertain traditional context, not guaranteed effect."
        ),
        "required_changes": [],
        "rejection_reason": "",
    }

    guard = build_pending_candidate_review_application_guard([draft], tmp_path)[0]
    markdown = render_pending_candidate_review_application_guard_markdown([draft], tmp_path)

    assert guard.ready_to_apply is True
    assert guard.preview_review_decision_delta == 1
    assert markdown.startswith("# Pending Candidate Review Application Guard")
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_application_packets_do_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_application_packets,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_application_packets_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_application_packets([draft], tmp_path)[0]
    markdown = render_pending_candidate_review_application_packets_markdown([draft], tmp_path)

    assert packet.ready_to_export is True
    assert packet.preview_review_decision_delta == 1
    assert markdown.startswith("# Pending Candidate Review Application Packets")
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_application_audit_summary_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_application_audit_summary,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_application_audit_summary_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    summary = build_pending_candidate_review_application_audit_summary([draft], tmp_path)
    markdown = render_pending_candidate_review_application_audit_summary_markdown(
        [draft], tmp_path)

    assert summary.packet_exportable_count == 1
    assert markdown.startswith("# Pending Candidate Review Application Audit Summary")
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_action_dashboard_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_action_dashboard,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_action_dashboard_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    dashboard = build_pending_candidate_review_manual_action_dashboard([draft], tmp_path)
    markdown = render_pending_candidate_review_manual_action_dashboard_markdown(
        [draft], tmp_path)

    assert dashboard.action_counts["apply_manual_application_packet"] == 1
    assert dashboard.applied_review_decision_delta == 0
    assert dashboard.applied_candidate_status_delta == 0
    assert dashboard.formal_evidence_delta == 0
    assert markdown.startswith("# Pending Candidate Review Manual Action Dashboard")
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_dry_run_guide_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_dry_run_guide,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_dry_run_guide_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    guide = build_pending_candidate_review_manual_application_dry_run_guide([draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_dry_run_guide_markdown(
        [draft], tmp_path)

    assert guide.step_count == 4
    assert guide.applied_review_decision_delta == 0
    assert guide.applied_candidate_status_delta == 0
    assert guide.formal_evidence_delta == 0
    assert markdown.startswith("# Pending Candidate Review Manual Application Dry-Run Guide")
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_preflight_report_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_preflight_report,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_preflight_report_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    report = build_pending_candidate_review_manual_application_preflight_report([draft], tmp_path)
    markdown = (
        render_pending_candidate_review_manual_application_preflight_report_markdown(
            [draft], tmp_path)
    )

    assert report.preflight_check_count == 4
    assert report.ready_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert report.applied_review_decision_delta == 0
    assert report.applied_candidate_status_delta == 0
    assert report.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Preflight Report"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_handoff_summary_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_handoff_summary,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_handoff_summary_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    summary = build_pending_candidate_review_manual_application_handoff_summary(
        [draft], tmp_path)
    markdown = (
        render_pending_candidate_review_manual_application_handoff_summary_markdown(
            [draft], tmp_path)
    )

    assert summary.handoff_item_count == 4
    assert summary.ready_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert summary.applied_review_decision_delta == 0
    assert summary.applied_candidate_status_delta == 0
    assert summary.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Handoff Summary"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_readiness_ledger_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_readiness_ledger,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_readiness_ledger_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    ledger = build_pending_candidate_review_manual_application_readiness_ledger(
        [draft], tmp_path)
    markdown = (
        render_pending_candidate_review_manual_application_readiness_ledger_markdown(
            [draft], tmp_path)
    )

    assert ledger.ledger_row_count == 4
    assert ledger.ready_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert ledger.applied_review_decision_delta == 0
    assert ledger.applied_candidate_status_delta == 0
    assert ledger.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Readiness Ledger"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_session_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_session_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_session_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_session_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_session_packet_markdown(
        [draft], tmp_path)

    assert packet.ready_action_count == 1
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Session Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_session_outcome_preview_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_session_outcome_preview,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_session_outcome_preview_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    preview = build_pending_candidate_review_manual_application_session_outcome_preview(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_session_outcome_preview_markdown(
        [draft], tmp_path)

    assert preview.ready_applied_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert preview.projected_review_decision_delta == 1
    assert preview.projected_candidate_status_delta == 1
    assert preview.applied_review_decision_delta == 0
    assert preview.applied_candidate_status_delta == 0
    assert preview.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Session Outcome Preview"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_post_session_verification_report_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_post_session_verification_report,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_post_session_verification_report_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    report = build_pending_candidate_review_manual_application_post_session_verification_report(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_post_session_verification_report_markdown(
        [draft], tmp_path)

    assert report.expected_ready_candidate_count == 1
    assert report.post_session_status == "blocked"
    assert report.applied_review_decision_delta == 0
    assert report.applied_candidate_status_delta == 0
    assert report.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Post-Session Verification Report"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_reconciliation_dashboard_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_reconciliation_dashboard,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    dashboard = build_pending_candidate_review_manual_application_reconciliation_dashboard(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_reconciliation_dashboard_markdown(
        [draft], tmp_path)

    assert dashboard.action_counts["append_missing_review_decision"] == 1
    assert dashboard.applied_review_decision_delta == 0
    assert dashboard.applied_candidate_status_delta == 0
    assert dashboard.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Reconciliation Dashboard"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_closure_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_closure_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_closure_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_closure_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_closure_packet_markdown(
        [draft], tmp_path)

    assert packet.closure_action_counts["carry_forward_missing_review_decision"] == 1
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Closure Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_starter_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_starter,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_starter_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    starter = build_pending_candidate_review_manual_application_next_session_starter(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_starter_markdown(
        [draft], tmp_path)

    assert starter.starter_lane_counts["missing_review_decision"] == 1
    assert starter.applied_review_decision_delta == 0
    assert starter.applied_candidate_status_delta == 0
    assert starter.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Starter"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_packet_markdown(
        [draft], tmp_path)

    assert packet.correction_candidate_ids == [
        "candidate_duan_ten_god_relation_017_001"
    ]
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_audit_summary_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_audit_summary,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_audit_summary_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    summary = build_pending_candidate_review_manual_application_next_session_audit_summary(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_audit_summary_markdown(
        [draft], tmp_path)

    assert summary.correction_queue_count == 1
    assert summary.coverage_checks["starter_to_packet_order"] == "covered"
    assert summary.applied_review_decision_delta == 0
    assert summary.applied_candidate_status_delta == 0
    assert summary.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Audit Summary"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_operator_checklist_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_operator_checklist,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    checklist = build_pending_candidate_review_manual_application_next_session_operator_checklist(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_operator_checklist_markdown(
        [draft], tmp_path)

    assert checklist.action_sequence[0] == "apply_correction_queue_first"
    assert checklist.applied_review_decision_delta == 0
    assert checklist.applied_candidate_status_delta == 0
    assert checklist.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Operator Checklist"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_execution_handoff_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_execution_handoff,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    handoff = build_pending_candidate_review_manual_application_next_session_execution_handoff(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_execution_handoff_markdown(
        [draft], tmp_path)

    assert handoff.first_action == "apply_correction_queue_first"
    assert handoff.applied_review_decision_delta == 0
    assert handoff.applied_candidate_status_delta == 0
    assert handoff.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Execution Handoff"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_completion_criteria_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_completion_criteria,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    criteria = build_pending_candidate_review_manual_application_next_session_completion_criteria(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_completion_criteria_markdown(
        [draft], tmp_path)

    assert criteria.first_action == "apply_correction_queue_first"
    assert criteria.applied_review_decision_delta == 0
    assert criteria.applied_candidate_status_delta == 0
    assert criteria.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Completion Criteria"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_retry_planner_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_retry_planner,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_retry_planner_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    planner = build_pending_candidate_review_manual_application_next_session_retry_planner(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_retry_planner_markdown(
        [draft], tmp_path)

    assert planner.first_action == "apply_correction_queue_first"
    assert planner.applied_review_decision_delta == 0
    assert planner.applied_candidate_status_delta == 0
    assert planner.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Retry Planner"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_final_readiness_summary_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_final_readiness_summary,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    summary = build_pending_candidate_review_manual_application_next_session_final_readiness_summary(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_final_readiness_summary_markdown(
        [draft], tmp_path)

    assert summary.readiness_status == "ready_to_start_next_manual_session"
    assert summary.applied_review_decision_delta == 0
    assert summary.applied_candidate_status_delta == 0
    assert summary.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Final Readiness Summary"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    note = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_note(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_note_markdown(
        [draft], tmp_path)

    assert note.launch_status == "ready_to_launch_manual_execution"
    assert note.applied_review_decision_delta == 0
    assert note.applied_candidate_status_delta == 0
    assert note.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Note"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_audit_markdown(
        [draft], tmp_path)

    assert audit.audit_status == "launch_audit_ready"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_manual_execution"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    runbook = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_markdown(
        [draft], tmp_path)

    assert runbook.runbook_status == "ready_for_manual_execution_runbook"
    assert runbook.applied_review_decision_delta == 0
    assert runbook.applied_candidate_status_delta == 0
    assert runbook.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_markdown(
        [draft], tmp_path)

    assert audit.audit_status == "runbook_audit_ready"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_runbook_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_manual_execution_runbook_audit"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Runbook Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_markdown(
        [draft], tmp_path)

    assert packet.launch_packet_status == "ready_for_final_manual_launch_packet"
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_markdown(
        [draft], tmp_path)

    assert audit.handoff_readiness == "ready_for_operator_handoff"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_final_launch_packet_handoff_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_operator_manual_execution_go"
    assert seal.go_no_go_decision == "go_for_operator_manual_execution"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Launch Packet Handoff Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    receipt = build_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_operator_go_no_go_seal_launch_receipt_markdown(
        [draft], tmp_path)

    assert receipt.receipt_status == "ready_for_operator_launch_receipt"
    assert receipt.receipt_decision == "receipt_ready_to_start_manual_execution"
    assert receipt.applied_review_decision_delta == 0
    assert receipt.applied_candidate_status_delta == 0
    assert receipt.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Go/No-Go Seal Launch Receipt"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_markdown(
        [draft], tmp_path)

    assert audit.final_boundary_readiness == "ready_for_final_boundary_audit"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_launch_receipt_final_boundary"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_markdown(
        [draft], tmp_path)

    assert packet.packet_status == "ready_for_operator_start_packet"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Launch Receipt Final Boundary Audit Seal Operator Start Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_operator_start_packet_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_markdown(
        [draft], tmp_path)

    assert audit.audit_status == "operator_start_packet_audit_ready"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Start Packet Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_operator_start_packet_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_launch_receipt_final_boundary_audit_seal_operator_start_packet_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_operator_start_packet_audit"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Operator Start Packet Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    receipt = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_markdown(
        [draft], tmp_path)

    assert receipt.receipt_status == "ready_for_manual_execution_start_authorization_receipt"
    assert receipt.applied_review_decision_delta == 0
    assert receipt.applied_candidate_status_delta == 0
    assert receipt.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_markdown(
        [draft], tmp_path)

    assert audit.coverage_audit_status == "start_authorization_receipt_coverage_audit_ready"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_receipt_coverage_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_start_authorization_receipt_coverage_audit"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Receipt Coverage Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_markdown(
        [draft], tmp_path)

    assert packet.packet_status == "ready_for_manual_execution_authorization_packet"
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_markdown(
        [draft], tmp_path)

    assert audit.audit_status == "manual_execution_authorization_packet_coverage_audit_ready"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_manual_execution_authorization_packet_coverage_audit"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    docket = build_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_authorization_packet_coverage_audit_seal_start_docket_markdown(
        [draft], tmp_path)

    assert docket.docket_status == "ready_for_manual_execution_start_docket"
    assert docket.applied_review_decision_delta == 0
    assert docket.applied_candidate_status_delta == 0
    assert docket.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Authorization Packet Coverage Audit Seal Start Docket"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_markdown(
        [draft], tmp_path)

    assert audit.audit_status == "manual_execution_start_docket_coverage_audit_ready"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_manual_execution_start_docket_coverage_audit"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Docket Coverage Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_docket_coverage_audit_seal_final_start_packet_markdown(
        [draft], tmp_path)

    assert packet.packet_status == "ready_for_manual_execution_final_start_packet"
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_markdown(
        [draft], tmp_path)

    assert audit.handoff_readiness == "ready_for_manual_execution_final_start_packet_handoff"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_manual_execution_final_start_packet_handoff"
    assert seal.go_no_go_start_decision == "go_for_operator_manual_execution"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Final Start Packet Handoff Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_final_start_packet_handoff_audit_seal_start_authorization_packet_markdown(
        [draft], tmp_path)

    assert packet.packet_status == "ready_for_manual_execution_start_authorization_packet"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_markdown(
        [draft], tmp_path)

    assert (
        audit.audit_status
        == "manual_execution_start_authorization_packet_coverage_audit_ready"
    )
    assert (
        audit.packet_status
        == "ready_for_manual_execution_start_authorization_packet"
    )
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_markdown(
        [draft], tmp_path)

    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_authorization_packet_coverage_audit"
    )
    assert (
        seal.audit_status
        == "manual_execution_start_authorization_packet_coverage_audit_ready"
    )
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Authorization Packet Coverage Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_markdown(
        [draft], tmp_path)

    assert packet.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert packet.start_authorization == "authorized_to_start_manual_execution"
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_coverage_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_markdown(
        [draft], tmp_path)

    assert (
        audit.audit_status
        == "manual_execution_start_clearance_packet_coverage_audit_ready"
    )
    assert audit.packet_status == "ready_for_manual_execution_start_clearance_packet"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_coverage_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_markdown(
        [draft], tmp_path)

    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_coverage_audit"
    )
    assert (
        seal.audit_status
        == "manual_execution_start_clearance_packet_coverage_audit_ready"
    )
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Coverage Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    authorization = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_markdown(
        [draft], tmp_path)

    assert (
        authorization.authorization_status
        == "authorized_for_manual_execution_start_from_clearance_packet"
    )
    assert (
        authorization.start_authorization == "authorized_to_start_manual_execution"
    )
    assert authorization.applied_review_decision_delta == 0
    assert authorization.applied_candidate_status_delta == 0
    assert authorization.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_markdown(
        [draft], tmp_path)

    assert (
        audit.audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert (
        audit.authorization_status
        == "authorized_for_manual_execution_start_from_clearance_packet"
    )
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_markdown(
        [draft], tmp_path)

    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_clearance_packet_final_start_authorization_coverage_audit"
    )
    assert (
        seal.audit_status
        == "manual_execution_start_clearance_packet_final_start_authorization_coverage_audit_ready"
    )
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_markdown(
        [draft], tmp_path)

    assert (
        packet.handoff_packet_status
        == "ready_for_manual_execution_start_handoff_packet"
    )
    assert (
        packet.handoff_status
        == "ready_for_operator_manual_execution_start_handoff"
    )
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Clearance Packet Final Start Authorization Coverage Audit Seal Start Handoff Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_markdown(
        [draft], tmp_path)

    assert audit.audit_status == "manual_execution_start_handoff_packet_coverage_audit_ready"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_handoff_packet_coverage_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_markdown(
        [draft], tmp_path)

    assert (
        seal.seal_status
        == "sealed_for_manual_execution_start_handoff_packet_coverage_audit"
    )
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Handoff Packet Coverage Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    packet = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_markdown(
        [draft], tmp_path)

    assert packet.start_packet_status == "ready_for_operator_manual_execution_start_packet"
    assert packet.applied_review_decision_delta == 0
    assert packet.applied_candidate_status_delta == 0
    assert packet.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_coverage_audit_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    audit = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_markdown(
        [draft], tmp_path)

    assert audit.audit_status == "manual_execution_start_packet_coverage_audit_ready"
    assert audit.applied_review_decision_delta == 0
    assert audit.applied_candidate_status_delta == 0
    assert audit.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_pending_candidate_review_manual_application_next_session_manual_execution_start_packet_coverage_audit_seal_does_not_write_review_decisions_or_evidence(tmp_path):
    _write_manual_application_fixture(tmp_path)
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_intake import (
        build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal,
        load_candidate_extracts,
        load_review_decisions,
        render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown,
    )

    before_candidate_statuses = {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    }
    before_decision_ids = {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }
    draft = {
        "decision_id": "review_candidate_duan_ten_god_relation_017_001",
        "candidate_id": "candidate_duan_ten_god_relation_017_001",
        "review_outcome": "returned",
        "reviewer": "maintainer",
        "reviewed_at": "2026-06-01",
        "source_locator": "learning-reference:note_duan_plain_mingxue_outline_001#lp_duan_ten_god_relation_001",
        "source_quality": "review_note",
        "confidence": "weak",
        "rationale": "Returned until source page or section locator is supplied.",
        "required_changes": ["Replace learning-reference locator before approval."],
        "approval_limitations": [],
        "rejection_reason": "",
    }

    seal = build_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal(
        [draft], tmp_path)
    markdown = render_pending_candidate_review_manual_application_next_session_manual_execution_start_authorization_packet_coverage_audit_seal_start_clearance_packet_coverage_audit_seal_final_start_authorization_coverage_audit_seal_start_handoff_packet_coverage_audit_seal_start_packet_coverage_audit_seal_markdown(
        [draft], tmp_path)

    assert seal.seal_status == "sealed_for_manual_execution_start_packet_coverage_audit"
    assert seal.applied_review_decision_delta == 0
    assert seal.applied_candidate_status_delta == 0
    assert seal.formal_evidence_delta == 0
    assert markdown.startswith(
        "# Pending Candidate Review Manual Application Next-Session Manual Execution Start Packet Coverage Audit Seal"
    )
    assert {
        candidate.candidate_id: candidate.status for candidate in load_candidate_extracts(tmp_path)
    } == before_candidate_statuses
    assert {
        decision.decision_id for decision in load_review_decisions(tmp_path)
    } == before_decision_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_report_evidence_loading_ignores_source_library_metadata(tmp_path):
    from mingli_engine.classical_sources import load_approved_evidence_units
    from mingli_engine.source_library import validate_source_library_quality

    classical_dir = tmp_path / "classical_sources"
    source_library_dir = tmp_path / "source_library"
    classical_dir.mkdir()
    source_library_dir.mkdir()
    for file_name in (
        "sources.json",
        "evidence_units.json",
        "curation_batches.json",
        "source_conflicts.json",
    ):
        (classical_dir / file_name).write_text("[]", encoding="utf-8")
    (source_library_dir / "source_library_entries.json").write_text(
        json.dumps(
            [
                {
                    "entry_id": "entry_planning_only",
                    "material_id": "material_planning_only",
                    "title": "Planning Only Source",
                    "material_type": "pdf",
                    "local_reference": "planning-only.pdf",
                    "tracking_status": "external_untracked",
                    "readiness_status": "not_started",
                    "topic_tags": [],
                    "rule_families": [],
                    "source_quality_notes": (
                        "Planning metadata that must never become report evidence."
                    ),
                    "rights_notes": "Do not copy long passages.",
                    "risk_tier": "ordinary",
                    "risk_notes": [],
                    "priority_level": "medium",
                    "next_action": "prepare_material",
                    "outcome_reason": "",
                    "created_at": "2026-05-28",
                    "updated_at": "2026-05-28",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (source_library_dir / "source_priority_assessments.json").write_text(
        "[]",
        encoding="utf-8",
    )
    (source_library_dir / "curation_batch_plans.json").write_text(
        json.dumps(
            [
                {
                    "batch_plan_id": "batch_plan_planning_only",
                    "title": "Planning Only Batch",
                    "goal": "Prepare planning material before extraction.",
                    "entry_ids": ["entry_planning_only"],
                    "target_gap_ids": ["gap_planning_only"],
                    "target_rule_families": [],
                    "risk_boundary": "ordinary",
                    "expected_output": ["formal_evidence"],
                    "status": "planned",
                    "review_capacity": "Small planning batch.",
                    "completion_summary": "",
                    "recommended_next_batch": "",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert load_approved_evidence_units(classical_dir) == []
    failures = validate_source_library_quality(source_library_dir)
    assert any("report evidence boundary" in failure for failure in failures)


def test_materials_audit_preparation_artifacts_do_not_become_formal_evidence(
    tmp_path,
):
    from mingli_engine import materials_audit
    from mingli_engine.classical_sources import load_approved_evidence_units

    classical_dir = tmp_path / "classical_sources"
    audit_dir = tmp_path / "materials_audit"
    classical_dir.mkdir()
    audit_dir.mkdir()
    for file_name in (
        "sources.json",
        "evidence_units.json",
        "curation_batches.json",
        "source_conflicts.json",
    ):
        (classical_dir / file_name).write_text("[]", encoding="utf-8")
    (audit_dir / "material_audit_records.json").write_text(
        json.dumps(
            [
                {
                    "audit_id": "audit_cleaned_markdown_boundary",
                    "canonical_title": "Cleaned Markdown Boundary",
                    "alternate_titles": ["Markdown/source_batch_001_cleaned"],
                    "material_scope": "bazi",
                    "primary_material_type": "markdown",
                    "representations": ["repr_cleaned_markdown_boundary"],
                    "source_library_entry_id": "",
                    "source_identity_confidence": "uncertain",
                    "preparation_state": "cleaned_text_available",
                    "source_boundary": "external_untracked",
                    "topic_tags": ["prepared-batch"],
                    "rule_families": [],
                    "risk_tier": "ordinary",
                    "risk_notes": [],
                    "rights_notes": "Preparation artifact only.",
                    "missing_prerequisites": ["source_library_alignment_review"],
                    "recommended_next_action": "register_source",
                    "outcome_reason": "",
                    "created_at": "2026-05-30",
                    "updated_at": "2026-05-30",
                },
                {
                    "audit_id": "audit_knowledge_skeleton_boundary",
                    "canonical_title": "Knowledge Skeleton Boundary",
                    "alternate_titles": ["资料整理/knowledge_skeleton/"],
                    "material_scope": "bazi",
                    "primary_material_type": "mixed",
                    "representations": ["repr_knowledge_skeleton_boundary"],
                    "source_library_entry_id": "",
                    "source_identity_confidence": "confirmed",
                    "preparation_state": "candidate_skeleton_available",
                    "source_boundary": "external_untracked",
                    "topic_tags": ["knowledge-skeleton"],
                    "rule_families": ["high_risk_signal"],
                    "risk_tier": "sensitive",
                    "risk_notes": ["Skeleton needs review before evidence promotion."],
                    "rights_notes": "Preparation artifact only.",
                    "missing_prerequisites": ["candidate_review"],
                    "recommended_next_action": "review_cleaned_text",
                    "outcome_reason": "",
                    "created_at": "2026-05-30",
                    "updated_at": "2026-05-30",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (audit_dir / "material_representations.json").write_text(
        json.dumps(
            [
                {
                    "representation_id": "repr_cleaned_markdown_boundary",
                    "audit_id": "audit_cleaned_markdown_boundary",
                    "representation_type": "cleaned_markdown",
                    "local_reference": "Markdown/source_batch_001_cleaned/",
                    "tracking_status": "external_untracked",
                    "text_quality": "cleaned",
                    "locator_quality": "folder_only",
                    "size_hint": "",
                    "modified_hint": "",
                    "contains_images": False,
                    "notes": "Cleaned Markdown remains a preparation aid.",
                },
                {
                    "representation_id": "repr_knowledge_skeleton_boundary",
                    "audit_id": "audit_knowledge_skeleton_boundary",
                    "representation_type": "knowledge_skeleton",
                    "local_reference": "资料整理/knowledge_skeleton/",
                    "tracking_status": "external_untracked",
                    "text_quality": "summary_only",
                    "locator_quality": "review_anchor",
                    "size_hint": "",
                    "modified_hint": "",
                    "contains_images": False,
                    "notes": "Knowledge skeleton remains a preparation aid.",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (audit_dir / "source_alignment_findings.json").write_text("[]", encoding="utf-8")
    (audit_dir / "preparation_readiness_findings.json").write_text(
        json.dumps(
            [
                {
                    "readiness_id": "ready_cleaned_markdown_boundary",
                    "audit_id": "audit_cleaned_markdown_boundary",
                    "readiness_state": "preparation_backlog",
                    "text_preparation_status": "cleaned",
                    "locator_confidence": "weak",
                    "source_quality": "moderate",
                    "risk_boundary": "ordinary",
                    "missing_prerequisites": ["source_library_registration"],
                    "ready_reasons": [],
                    "blockers": [
                        "Cleaned Markdown must not be treated as formal report evidence."
                    ],
                    "recommended_next_action": "register_source",
                    "assessed_by": "maintainer",
                    "assessed_at": "2026-05-30",
                },
                {
                    "readiness_id": "ready_knowledge_skeleton_boundary",
                    "audit_id": "audit_knowledge_skeleton_boundary",
                    "readiness_state": "preparation_backlog",
                    "text_preparation_status": "summary_only",
                    "locator_confidence": "moderate",
                    "source_quality": "needs_recheck",
                    "risk_boundary": "sensitive",
                    "missing_prerequisites": ["candidate_review"],
                    "ready_reasons": [],
                    "blockers": [
                        "Knowledge skeleton must not become a report-usable evidence unit."
                    ],
                    "recommended_next_action": "review_cleaned_text",
                    "assessed_by": "maintainer",
                    "assessed_at": "2026-05-30",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (audit_dir / "extraction_queue_items.json").write_text("[]", encoding="utf-8")

    assert load_approved_evidence_units(classical_dir) == []
    failures = materials_audit.validate_materials_audit_quality(audit_dir)
    assert any("report evidence boundary" in failure for failure in failures)


def test_materials_audit_queue_items_do_not_change_formal_evidence_counts(
    tmp_path,
):
    from mingli_engine import materials_audit
    from mingli_engine.classical_sources import load_approved_evidence_units

    classical_dir = tmp_path / "classical_sources"
    audit_dir = tmp_path / "materials_audit"
    classical_dir.mkdir()
    audit_dir.mkdir()
    for file_name in (
        "sources.json",
        "evidence_units.json",
        "curation_batches.json",
        "source_conflicts.json",
    ):
        (classical_dir / file_name).write_text("[]", encoding="utf-8")
    (audit_dir / "material_audit_records.json").write_text(
        json.dumps(
            [
                {
                    "audit_id": "audit_queue_boundary",
                    "canonical_title": "Queue Boundary",
                    "alternate_titles": [],
                    "material_scope": "bazi",
                    "primary_material_type": "markdown",
                    "representations": ["repr_queue_boundary"],
                    "source_library_entry_id": "",
                    "source_identity_confidence": "uncertain",
                    "preparation_state": "cleaned_text_available",
                    "source_boundary": "external_untracked",
                    "topic_tags": ["prepared-batch"],
                    "rule_families": [],
                    "risk_tier": "ordinary",
                    "risk_notes": [],
                    "rights_notes": "Preparation artifact only.",
                    "missing_prerequisites": ["source_library_registration"],
                    "recommended_next_action": "register_source",
                    "outcome_reason": "",
                    "created_at": "2026-05-30",
                    "updated_at": "2026-05-30",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (audit_dir / "material_representations.json").write_text(
        json.dumps(
            [
                {
                    "representation_id": "repr_queue_boundary",
                    "audit_id": "audit_queue_boundary",
                    "representation_type": "cleaned_markdown",
                    "local_reference": "Markdown/source_batch_boundary_cleaned/",
                    "tracking_status": "external_untracked",
                    "text_quality": "cleaned",
                    "locator_quality": "folder_only",
                    "size_hint": "",
                    "modified_hint": "",
                    "contains_images": False,
                    "notes": "Queue item remains planning metadata only.",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (audit_dir / "source_alignment_findings.json").write_text("[]", encoding="utf-8")
    (audit_dir / "preparation_readiness_findings.json").write_text(
        json.dumps(
            [
                {
                    "readiness_id": "ready_queue_boundary",
                    "audit_id": "audit_queue_boundary",
                    "readiness_state": "needs_source_registration",
                    "text_preparation_status": "cleaned",
                    "locator_confidence": "moderate",
                    "source_quality": "moderate",
                    "risk_boundary": "ordinary",
                    "missing_prerequisites": ["source_library_registration"],
                    "ready_reasons": [],
                    "blockers": [
                        "Source-library registration is required before extraction."
                    ],
                    "recommended_next_action": "register_source",
                    "assessed_by": "maintainer",
                    "assessed_at": "2026-05-30",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (audit_dir / "extraction_queue_items.json").write_text(
        json.dumps(
            [
                {
                    "queue_item_id": "queue_boundary_register",
                    "audit_id": "audit_queue_boundary",
                    "queue_type": "registration_backlog",
                    "priority_level": "medium",
                    "priority_rationale": (
                        "Register the cleaned Markdown source before extraction."
                    ),
                    "target_rule_families": [],
                    "target_gap_ids": [],
                    "risk_boundary": "ordinary",
                    "pre_extraction_checks": ["create source-library registration"],
                    "recommended_action": "register_source",
                    "depends_on": ["source_library_registration"],
                    "status": "planned",
                    "created_at": "2026-05-30",
                    "updated_at": "2026-05-30",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert load_approved_evidence_units(classical_dir) == []
    summary = materials_audit.build_materials_audit_progress_summary(audit_dir)
    assert summary.registration_backlog_count == 1
    assert load_approved_evidence_units(classical_dir) == []


def test_candidate_draft_slots_do_not_change_candidate_or_formal_evidence_counts(
    tmp_path,
):
    from mingli_engine import extraction_queue_intake, source_intake
    from mingli_engine.classical_sources import load_approved_evidence_units

    classical_dir = tmp_path / "classical_sources"
    intake_dir = tmp_path / "source_intake"
    extraction_dir = tmp_path / "extraction_queue_intake"
    classical_dir.mkdir()
    intake_dir.mkdir()
    extraction_dir.mkdir()
    for file_name in (
        "sources.json",
        "evidence_units.json",
        "curation_batches.json",
        "source_conflicts.json",
    ):
        (classical_dir / file_name).write_text("[]", encoding="utf-8")
    (intake_dir / "source_materials.json").write_text(
        json.dumps(
            [
                {
                    "material_id": "material_boundary",
                    "title": "Boundary Material",
                    "material_type": "pdf",
                    "file_label": "boundary.pdf",
                    "tracking_status": "external_untracked",
                    "preparation_status": "partially_reviewed",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    for file_name in (
        "candidate_extracts.json",
        "review_decisions.json",
        "promotion_batches.json",
    ):
        (intake_dir / file_name).write_text("[]", encoding="utf-8")
    (extraction_dir / "extraction_work_packages.json").write_text(
        json.dumps(
            [
                {
                    "package_id": "package_boundary",
                    "package_label": "Boundary package",
                    "source_queue_snapshot_ids": ["queue_boundary"],
                    "selected_task_ids": ["task_boundary"],
                    "backlog_record_ids": [],
                    "status": "planned",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                    "notes": "Draft slots are planning metadata only.",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (extraction_dir / "extraction_tasks.json").write_text(
        json.dumps(
            [
                {
                    "task_id": "task_boundary",
                    "package_id": "package_boundary",
                    "queue_item_id": "queue_boundary",
                    "audit_id": "audit_boundary",
                    "source_library_entry_id": "entry_boundary",
                    "intended_source_material_id": "material_boundary",
                    "priority_level": "medium",
                    "priority_rationale": "Ready boundary task.",
                    "target_rule_families": ["blind_image_method"],
                    "target_gap_ids": [],
                    "risk_boundary": "ordinary",
                    "locator_requirement": "page_or_section",
                    "source_quality_note": "Review before extraction.",
                    "rights_note": "Do not copy long passages.",
                    "pre_extraction_checks": ["confirm source locator"],
                    "overlap_warnings": [],
                    "recommended_action": "extract_candidates",
                    "status": "planned",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (extraction_dir / "candidate_draft_slots.json").write_text(
        json.dumps(
            [
                {
                    "draft_slot_id": "slot_boundary",
                    "task_id": "task_boundary",
                    "intended_candidate_label": "Future boundary candidate",
                    "target_rule_family": "blind_image_method",
                    "target_gap_id": "",
                    "locator_requirement": "page_or_section",
                    "expected_review_notes": ["Record locator during manual extraction."],
                    "risk_boundary": "ordinary",
                    "safety_requirements": ["No absolute destiny language."],
                    "status": "planned",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (extraction_dir / "prerequisite_backlog_records.json").write_text(
        "[]",
        encoding="utf-8",
    )

    assert len(source_intake.load_candidate_extracts(intake_dir)) == 0
    assert len(load_approved_evidence_units(classical_dir)) == 0
    slots = extraction_queue_intake.load_candidate_draft_slots(extraction_dir)
    assert [slot.draft_slot_id for slot in slots] == ["slot_boundary"]
    assert len(source_intake.load_candidate_extracts(intake_dir)) == 0
    assert len(load_approved_evidence_units(classical_dir)) == 0


def test_extraction_queue_intake_records_do_not_change_formal_evidence_counts(
    tmp_path,
):
    from mingli_engine import extraction_queue_intake, source_intake
    from mingli_engine.classical_sources import load_approved_evidence_units

    classical_dir = tmp_path / "classical_sources"
    intake_dir = tmp_path / "source_intake"
    extraction_dir = tmp_path / "extraction_queue_intake"
    classical_dir.mkdir()
    intake_dir.mkdir()
    extraction_dir.mkdir()
    for file_name in (
        "sources.json",
        "evidence_units.json",
        "curation_batches.json",
        "source_conflicts.json",
    ):
        (classical_dir / file_name).write_text("[]", encoding="utf-8")
    (intake_dir / "source_materials.json").write_text(
        json.dumps(
            [
                {
                    "material_id": "material_boundary",
                    "title": "Boundary Material",
                    "material_type": "pdf",
                    "file_label": "boundary.pdf",
                    "tracking_status": "external_untracked",
                    "preparation_status": "partially_reviewed",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    for file_name in (
        "candidate_extracts.json",
        "review_decisions.json",
        "promotion_batches.json",
    ):
        (intake_dir / file_name).write_text("[]", encoding="utf-8")
    (extraction_dir / "extraction_work_packages.json").write_text(
        json.dumps(
            [
                {
                    "package_id": "package_boundary",
                    "package_label": "Boundary package",
                    "source_queue_snapshot_ids": [
                        "queue_task_boundary",
                        "queue_backlog_boundary",
                    ],
                    "selected_task_ids": ["task_boundary"],
                    "backlog_record_ids": ["backlog_boundary"],
                    "status": "planned",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                    "notes": "Extraction queue records are planning metadata only.",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (extraction_dir / "extraction_tasks.json").write_text(
        json.dumps(
            [
                {
                    "task_id": "task_boundary",
                    "package_id": "package_boundary",
                    "queue_item_id": "queue_task_boundary",
                    "audit_id": "audit_task_boundary",
                    "source_library_entry_id": "entry_boundary",
                    "intended_source_material_id": "material_boundary",
                    "priority_level": "medium",
                    "priority_rationale": "Ready boundary task.",
                    "target_rule_families": ["blind_image_method"],
                    "target_gap_ids": [],
                    "risk_boundary": "ordinary",
                    "locator_requirement": "page_or_section",
                    "source_quality_note": "Review before extraction.",
                    "rights_note": "Do not copy long passages.",
                    "pre_extraction_checks": ["confirm source locator"],
                    "overlap_warnings": [],
                    "recommended_action": "extract_candidates",
                    "status": "planned",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (extraction_dir / "candidate_draft_slots.json").write_text(
        json.dumps(
            [
                {
                    "draft_slot_id": "slot_boundary",
                    "task_id": "task_boundary",
                    "intended_candidate_label": "Future boundary candidate",
                    "target_rule_family": "blind_image_method",
                    "target_gap_id": "",
                    "locator_requirement": "page_or_section",
                    "expected_review_notes": ["Record locator during manual extraction."],
                    "risk_boundary": "ordinary",
                    "safety_requirements": ["No absolute destiny language."],
                    "status": "planned",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (extraction_dir / "prerequisite_backlog_records.json").write_text(
        json.dumps(
            [
                {
                    "backlog_id": "backlog_boundary",
                    "package_id": "package_boundary",
                    "queue_item_id": "queue_backlog_boundary",
                    "audit_id": "audit_backlog_boundary",
                    "backlog_type": "registration",
                    "missing_prerequisites": ["source_library_registration"],
                    "durable_reason": (
                        "Source-library registration is required before extraction."
                    ),
                    "recommended_action": "register_source",
                    "risk_boundary": "ordinary",
                    "status": "planned",
                    "created_at": "2026-05-31",
                    "updated_at": "2026-05-31",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert len(source_intake.load_candidate_extracts(intake_dir)) == 0
    assert len(load_approved_evidence_units(classical_dir)) == 0
    assert extraction_queue_intake.load_extraction_work_packages(extraction_dir)
    assert extraction_queue_intake.load_extraction_tasks(extraction_dir)
    assert extraction_queue_intake.load_candidate_draft_slots(extraction_dir)
    assert extraction_queue_intake.load_prerequisite_backlog_records(extraction_dir)
    assert len(source_intake.load_candidate_extracts(intake_dir)) == 0
    assert len(load_approved_evidence_units(classical_dir)) == 0


def test_learning_reference_intake_decisions_do_not_change_candidate_or_formal_evidence_counts():
    from mingli_engine import learning_reference_curation, source_intake
    from mingli_engine.classical_sources import load_approved_evidence_units

    before_candidate_ids = {
        candidate.candidate_id for candidate in source_intake.load_candidate_extracts()
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    points = learning_reference_curation.load_learning_points()
    decisions = learning_reference_curation.load_candidate_intake_decisions()

    assert len(points) == 43
    assert len(decisions) == 37
    assert {
        "lp_northeast_blind_image_001",
        "lp_mingli_pattern_strength_001",
        "lp_duan_ten_god_relation_001",
        "lp_mingxue_five_element_balance_001",
        "lp_hongfu_remedy_boundary_001",
        "lp_markdown_batch_002_useful_god_001",
        "lp_liang_tianyuan_wuxian_day_master_use_god_001",
        "lp_liang_yushi_month_branch_use_god_taxonomy_001",
        "lp_bazi_general_lecture_pattern_strength_001",
        "lp_bazi_general_beichen_branch_interaction_001",
        "lp_bazi_general_ziping_useful_god_001",
        "lp_bazi_general_ditiansui_pattern_strength_001",
        "lp_bazi_general_qiongtong_useful_god_001",
        "lp_bazi_general_true_spirit_useful_god_001",
        "lp_bazi_general_wangdoujing_branch_interaction_001",
    }.issubset({point.learning_point_id for point in points})
    assert {
        "decision_northeast_blind_image_001",
        "decision_mingli_pattern_strength_001",
        "decision_duan_ten_god_relation_001",
        "decision_mingxue_five_element_balance_001",
        "decision_hongfu_remedy_boundary_001",
        "decision_markdown_batch_002_useful_god_001",
        "decision_liang_tianyuan_wuxian_reuse_batch004_pattern_001",
        "decision_liang_yushi_yongshen_reuse_batch004_useful_god_001",
        "decision_bazi_general_lecture_pattern_strength_001",
        "decision_bazi_general_beichen_branch_interaction_001",
        "decision_bazi_general_ziping_useful_god_001",
        "decision_bazi_general_ditiansui_pattern_strength_001",
        "decision_bazi_general_qiongtong_useful_god_001",
        "decision_bazi_general_true_spirit_useful_god_001",
        "decision_bazi_general_wangdoujing_branch_interaction_001",
    }.issubset({decision.decision_id for decision in decisions})
    assert {
        candidate.candidate_id for candidate in source_intake.load_candidate_extracts()
    } == before_candidate_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_learning_reference_prerequisite_actions_do_not_change_formal_evidence_counts():
    from mingli_engine import learning_reference_curation, source_intake
    from mingli_engine.classical_sources import load_approved_evidence_units

    before_candidate_ids = {
        candidate.candidate_id for candidate in source_intake.load_candidate_extracts()
    }
    before_formal_evidence_ids = {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    }

    notes = learning_reference_curation.load_learning_reference_notes()
    points = learning_reference_curation.load_learning_points()
    decisions = learning_reference_curation.load_candidate_intake_decisions()
    action_notes = learning_reference_curation.load_prerequisite_action_notes()
    summary = learning_reference_curation.build_learning_reference_progress_summary()

    assert notes
    assert points
    assert decisions
    assert {action.action_note_id for action in action_notes} == {
        "action_blind_life_manual_risk_review_001",
        "action_blind_school_secret_blocked_001",
        "action_markdown_batch_003_registration_001",
        "action_immortal_fortune_jianghu_secret_risk_review_001",
        "action_life_death_book_100_pages_risk_review_001",
        "action_source_processing_status_deferred_001",
        "action_markdown_batch_005_risk_review_001",
    }
    assert summary.formal_evidence_delta == 0
    assert summary.note_counts == {"candidate_intake_started": 23}
    assert summary.learning_point_counts == {
        "duplicate_review": 3,
        "ready": 34,
        "deferred": 6,
    }
    assert summary.candidate_decision_count == 37
    assert summary.candidate_ready_count == 34
    assert summary.prerequisite_action_counts == {
        "risk_review": 4,
        "blocked": 1,
        "deferred": 2,
        "status:completed": 4,
        "status:blocked": 1,
        "status:deferred": 2,
    }
    assert {
        candidate.candidate_id for candidate in source_intake.load_candidate_extracts()
    } == before_candidate_ids
    assert {
        evidence.evidence_id for evidence in load_approved_evidence_units()
    } == before_formal_evidence_ids


def test_safety_json_regression_cases_keep_refusal_contracts():
    for case in _safety_json_cases():
        result = _run_cli(
            case["command"],
            "--input",
            str(REPO_ROOT / case["input"]),
            "--format",
            "markdown",
        )
        _assert_safety_json(case, result)
