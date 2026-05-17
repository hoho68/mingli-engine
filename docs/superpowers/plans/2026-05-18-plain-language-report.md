# Plain-Language Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make generated Bazi Markdown reports read like plain Chinese reports by translating selected machine-facing values and polishing key wording without changing calculations, CLI behavior, safety rules, or the 004 layered structure.

**Architecture:** Keep all wording preparation in `src/mingli_engine/report_schema.py`, where chart and interpretation objects already become report text. Keep `src/mingli_engine/markdown.py` as a layout-only boundary and preserve the 004 heading order. Tests drive the change at schema, integration, renderer, and safety levels.

**Tech Stack:** Python 3.12+, dataclasses, existing CLI/report modules, pytest, no new runtime dependencies.

---

## File Structure

- Modify: `src/mingli_engine/report_schema.py`
  - Add small reader-facing label helpers and use them while building chart card, assumptions, four-pillar summary, quick guide, and action-reflection wording.
- Modify: `tests/unit/test_report_schema.py`
  - Verify labels, fallback behavior, quick-guide wording, and absence of selected raw labels in report fields.
- Modify: `tests/unit/test_markdown_renderer.py`
  - Keep heading-order coverage unchanged and add a guard that the renderer still emits the 004 sequence after wording changes.
- Modify: `tests/integration/test_calculate_report_cli.py`
  - Verify automatic chart CLI output uses plain-language labels and no selected raw labels.
- Modify: `tests/integration/test_generate_markdown_report.py`
  - Verify external chart CLI output uses plain-language labels and no selected raw labels.
- Modify: `tests/safety/test_red_lines_and_language.py`
  - Preserve generated-report prohibited-language and red-line behavior after wording changes.

## Task 1: Add Schema-Level Plain-Language Tests

**Files:**
- Modify: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Add a raw-label assertion helper**

Add near the imports in `tests/unit/test_report_schema.py`:

```python
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


def _report_body(report) -> str:
    return "\n".join(
        [
            report.quick_guide,
            report.chart_card,
            report.assumptions,
            report.four_pillars_summary,
            report.five_elements_summary,
            report.ten_gods_summary,
            report.structure_analysis,
            report.personality_tendencies,
            report.strengths_and_issues,
            report.phase_overview,
            report.action_suggestions,
            report.interpretation_boundaries,
        ]
    )
```

- [ ] **Step 2: Add failing test for reader-facing labels**

Append:

```python
def test_build_report_uses_reader_facing_labels(sample_bazi_chart):
    report = build_report(sample_bazi_chart)
    body = _report_body(report)

    assert "公历" in report.chart_card
    assert "系统自动排盘" in report.quick_guide
    assert "系统自动排盘" in report.assumptions
    assert "中等可信度" in report.quick_guide
    assert "中等可信度" in report.assumptions
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert f"- {pillar_name}：" in report.four_pillars_summary
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in body
```

- [ ] **Step 3: Add failing test for fallback wording**

Append:

```python
def test_build_report_uses_conservative_placeholder_for_unspecified_gender(
    sample_bazi_chart,
):
    report = build_report(sample_bazi_chart)

    assert "性别标记：未说明" in report.chart_card
```

- [ ] **Step 4: Update existing quick-guide assertions**

In `test_build_report_prepares_quick_guide_and_boundary_layer`, replace:

```python
    assert sample_bazi_chart.chart_source.source_type in report.quick_guide
    assert sample_bazi_chart.chart_source.confidence in report.quick_guide
```

with:

```python
    assert "系统自动排盘" in report.quick_guide
    assert "中等可信度" in report.quick_guide
```

- [ ] **Step 5: Run tests and verify failure**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py -v
```

Expected: the new label tests fail because the report still exposes raw labels.

## Task 2: Implement Reader-Facing Label Helpers

**Files:**
- Modify: `src/mingli_engine/report_schema.py`
- Modify: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Add mapping constants and helpers**

In `src/mingli_engine/report_schema.py`, after `LIFESPAN_FOCUS_TOPICS`, add:

```python
CALENDAR_TYPE_LABELS = {
    "gregorian": "公历",
}

SOURCE_TYPE_LABELS = {
    "auto_calculated": "系统自动排盘",
    "external_verified": "外部排盘已核对",
}

CONFIDENCE_LABELS = {
    "low": "低可信度",
    "medium": "中等可信度",
    "high": "高可信度",
}

PILLAR_NAME_LABELS = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "hour": "时柱",
}

UNSPECIFIED_VALUES = frozenset({"", "未指定", "unspecified", "unknown", "none"})


def _reader_label(value: str | None, labels: dict[str, str]) -> str:
    normalized = "" if value is None else str(value).strip()
    if normalized.lower() in UNSPECIFIED_VALUES:
        return "未说明"
    return labels.get(normalized, normalized)
```

- [ ] **Step 2: Use helper in chart card**

Update `_build_chart_card`:

```python
def _build_chart_card(chart: BaziChart) -> str:
    profile = chart.birth_profile
    return "\n".join(
        [
            f"- 历法类型：{_reader_label(profile.calendar_type, CALENDAR_TYPE_LABELS)}",
            f"- 出生日期：{profile.birth_date}",
            f"- 出生时间：{profile.birth_time}",
            f"- 出生地点：{profile.birthplace}",
            f"- 性别标记：{_reader_label(profile.gender, {})}",
            f"- 关注主题：{profile.focus_topic or '未说明'}",
            f"- 日主：{chart.day_master}",
        ]
    )
```

- [ ] **Step 3: Use helper in assumptions**

Update `_build_assumptions`:

```python
def _build_assumptions(chart: BaziChart) -> str:
    source = chart.chart_source
    return "\n".join(
        [
            f"- 来源类型：{_reader_label(source.source_type, SOURCE_TYPE_LABELS)}",
            f"- 来源说明：{source.source_note}",
            f"- 历法假设：{source.calendar_assumption}",
            f"- 时区假设：{source.timezone_assumption}",
            f"- 节气假设：{source.solar_terms_assumption}",
            f"- 真太阳时：{_format_true_solar_time(source.true_solar_time_applied)}",
            f"- 可信度：{_reader_label(source.confidence, CONFIDENCE_LABELS)}",
        ]
    )
```

- [ ] **Step 4: Use helper in four-pillar summary**

Update `_build_four_pillars_summary`:

```python
def _build_four_pillars_summary(chart: BaziChart) -> str:
    rows = []
    for pillar in chart.pillars:
        hidden_stems = "、".join(pillar.hidden_stems) if pillar.hidden_stems else "无"
        pillar_name = _reader_label(pillar.name, PILLAR_NAME_LABELS)
        rows.append(
            f"- {pillar_name}：{pillar.heavenly_stem}{pillar.earthly_branch}，"
            f"藏干：{hidden_stems}，十神：{pillar.ten_god}，五行：{pillar.element}"
        )
    return "\n".join(rows)
```

- [ ] **Step 5: Run schema tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py -v
```

Expected: tests still fail only on quick-guide wording if Task 3 has not been implemented yet.

- [ ] **Step 6: Commit Task 2**

Commit only if the schema tests pass. If they still fail because Task 3 is needed, do not commit yet; continue to Task 3 and commit both label helpers and wording together.

## Task 3: Polish Quick Guide And Key Report Wording

**Files:**
- Modify: `src/mingli_engine/report_schema.py`
- Modify: `tests/unit/test_report_schema.py`

- [ ] **Step 1: Add test for plain quick-guide wording**

Append to `tests/unit/test_report_schema.py`:

```python
def test_build_report_quick_guide_reads_like_plain_guidance(sample_bazi_chart):
    report = build_report(sample_bazi_chart)

    assert "这份盘的资料来自系统自动排盘" in report.quick_guide
    assert "这份盘里" in report.quick_guide
    assert "适合先从" in report.quick_guide
    assert "不是命运结论" in report.quick_guide
    assert "可复盘的小问题" in report.quick_guide
```

- [ ] **Step 2: Update quick-guide builder**

Replace `_build_quick_guide` with:

```python
def _build_quick_guide(chart: BaziChart, interpretation) -> str:
    source = chart.chart_source
    focus_topic = chart.birth_profile.focus_topic.strip() or "当前关注主题"
    source_label = _reader_label(source.source_type, SOURCE_TYPE_LABELS)
    confidence_label = _reader_label(source.confidence, CONFIDENCE_LABELS)
    dominant = _format_elements_for_report(
        interpretation.element_distribution.dominant_elements
    )
    return "\n".join(
        [
            f"- 来源：这份盘的资料来自{source_label}，当前标记为{confidence_label}。",
            f"- 结构：这份盘里，{dominant}的信号比较集中，适合先从这些方向看整体结构。",
            f"- 日主：{chart.day_master}是本报告的观察中心，不是命运结论。",
            "- 边界：本报告不做格局定论、用神定论或大运流年判断。",
            f"- 提示：围绕{focus_topic}，把结构观察转成可复盘的小问题。",
        ]
    )
```

- [ ] **Step 3: Polish action suggestion wording**

Replace the `action_suggestions = (...)` block in `build_report` with:

```python
    action_suggestions = (
        f"围绕{focus_topic}，可以先承接{action_focus}，整理成一两个可记录的小步骤，"
        "再用现实反馈慢慢复盘。这里给的是观察和整理方向，不是对结果的承诺。"
    )
```

- [ ] **Step 4: Run schema tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py -v
```

Expected: all report schema tests pass.

- [ ] **Step 5: Commit Tasks 2 and 3 together if Task 2 was not committed**

Run:

```powershell
git add src\mingli_engine\report_schema.py tests\unit\test_report_schema.py
git commit -m "feat: polish report labels and guidance"
```

## Task 4: Update CLI And Safety Coverage

**Files:**
- Modify: `tests/integration/test_calculate_report_cli.py`
- Modify: `tests/integration/test_generate_markdown_report.py`
- Modify: `tests/safety/test_red_lines_and_language.py`
- Modify: `tests/unit/test_markdown_renderer.py`

- [ ] **Step 1: Add raw-label helper to CLI integration tests**

In both integration test files, add:

```python
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


def _assert_plain_language_report(markdown: str) -> None:
    assert "公历" in markdown
    for pillar_name in ("年柱", "月柱", "日柱", "时柱"):
        assert f"- {pillar_name}：" in markdown
    for raw_label in RAW_READER_LABELS:
        assert raw_label not in markdown
```

- [ ] **Step 2: Update automatic chart integration assertions**

In `tests/integration/test_calculate_report_cli.py`, replace:

```python
    assert "auto_calculated" in markdown
    assert "medium" in markdown
```

with:

```python
    _assert_plain_language_report(markdown)
    assert "系统自动排盘" in markdown
    assert "中等可信度" in markdown
```

- [ ] **Step 3: Update external chart integration assertions**

In `tests/integration/test_generate_markdown_report.py`, add after source-note assertion:

```python
    _assert_plain_language_report(markdown)
    assert "外部排盘已核对" in markdown
```

- [ ] **Step 4: Preserve renderer heading test**

In `tests/unit/test_markdown_renderer.py`, do not change expected heading order. If any assertion still expects raw labels, update it to reader-facing labels.

- [ ] **Step 5: Strengthen safety generated-report coverage**

In `tests/safety/test_red_lines_and_language.py`, inside `test_generated_auto_report_avoids_absolute_or_fatalistic_phrases`, after `markdown = result.stdout`, add:

```python
    assert "系统自动排盘" in markdown
    assert "中等可信度" in markdown
    for raw_label in ("auto_calculated", "medium", "gregorian"):
        assert raw_label not in markdown
```

- [ ] **Step 6: Run integration and safety tests**

Run:

```powershell
uv run --with pytest python -m pytest tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py tests\safety\test_red_lines_and_language.py tests\unit\test_markdown_renderer.py -v
```

Expected: all selected tests pass, including existing exit code `3` safety cases.

- [ ] **Step 7: Commit Task 4**

Run:

```powershell
git add tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py tests\safety\test_red_lines_and_language.py tests\unit\test_markdown_renderer.py
git commit -m "test: cover plain-language report output"
```

## Task 5: Full Verification

**Files:**
- Read: `specs/005-plain-language-report/spec.md`
- Read: `specs/005-plain-language-report/contracts/plain-language-markdown-contract.md`

- [ ] **Step 1: Run focused verification**

Run:

```powershell
uv run --with pytest python -m pytest tests\unit\test_report_schema.py tests\unit\test_markdown_renderer.py tests\integration\test_generate_markdown_report.py tests\integration\test_calculate_report_cli.py tests\safety\test_red_lines_and_language.py -v
```

Expected: all selected tests pass.

- [ ] **Step 2: Run the full suite**

Run:

```powershell
uv run --with pytest python -m pytest
```

Expected: all tests pass.

- [ ] **Step 3: Inspect automatic generated Markdown manually**

Run:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli calculate-report --input examples\birth-profile.auto-gregorian.json --format markdown
```

Expected output includes `系统自动排盘`, `中等可信度`, `公历`, `年柱`, `月柱`, `日柱`, and `时柱`; it does not include `auto_calculated`, `medium`, `gregorian`, `year：`, `month：`, `day：`, or `hour：`.

- [ ] **Step 4: Inspect external generated Markdown manually**

Run:

```powershell
$env:PYTHONPATH='src'
uv run python -m mingli_engine.cli generate-report --input examples\bazi-chart.external-verified.json --format markdown
```

Expected output includes `外部排盘已核对` and the external source note; it does not include `external_verified`.

- [ ] **Step 5: Confirm worktree status**

Run:

```powershell
git status --short --branch
```

Expected: branch is `005-plain-language-report` with no uncommitted implementation changes.
