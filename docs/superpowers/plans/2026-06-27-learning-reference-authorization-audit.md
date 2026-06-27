# Learning Reference Authorization Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local 017 authorization audit packet that verifies closed learning notes, applied candidate-intake decisions, 013 downstream state, and 012 formal evidence are aligned before any optional downstream work.

**Architecture:** Add one read-only dataclass and two 017 helper functions. The builder derives all counts from existing loaders and returns an explicit authorization status; the renderer emits Markdown markers used by overview, quickstart, and handoff docs. No JSON candidate/review/promotion/formal evidence data is mutated.

**Tech Stack:** Python 3.12, project-local JSON loaders, pytest, Markdown documentation.

---

### Task 1: Lock the Authorization Audit API

**Files:**
- Modify: `tests/unit/test_learning_reference_curation.py`

- [x] **Step 1: Write the failing audit-builder test**

Add:

```python
def test_learning_reference_authorization_audit_confirms_local_boundary_clearance():
    audit = learning_reference_curation.build_learning_reference_authorization_audit()

    assert audit.audit_id == "017-candidate-formal-evidence-authorization-audit"
    assert audit.authorization_status == "ready_for_explicit_downstream_authorization"
    assert audit.downstream_mutation_authorized is False
    assert audit.note_counts == {"candidate_intake_started": 14}
    assert audit.next_action_ids == []
    assert audit.decision_counts == {
        "reuse_existing": 1,
        "create_candidate": 27,
        "status:applied": 28,
    }
    assert audit.candidate_status_counts == {
        "promoted": 32,
        "rejected": 2,
        "returned": 1,
        "blocked": 1,
    }
    assert audit.review_decision_counts == {
        "approved": 32,
        "rejected": 2,
        "returned": 1,
        "blocked": 1,
    }
    assert audit.promotion_review_status_counts == {"reviewed": 25}
    assert audit.formal_evidence_unit_count == 92
    assert audit.formal_evidence_delta == 0
    assert audit.leakage_counts == {
        "learning_reference_source_refs_in_012": 0,
        "candidate_id_source_refs_in_012": 0,
        "learning_closure_source_refs_in_012": 0,
    }
    assert audit.clearance_checks == {
        "017_notes_closed": "passed",
        "017_no_active_next_actions": "passed",
        "017_decisions_applied": "passed",
        "013_candidate_review_promotion_counts_aligned": "passed",
        "012_formal_evidence_boundary_clean": "passed",
        "downstream_mutation_requires_explicit_request": "passed",
    }
```

- [x] **Step 2: Write the failing renderer/docs test**

Add:

```python
def test_learning_reference_authorization_audit_markdown_and_docs_are_in_sync():
    audit = learning_reference_curation.build_learning_reference_authorization_audit()
    markdown = learning_reference_curation.render_learning_reference_authorization_audit_markdown(audit)
    overview = Path("docs/classical_sources/learning_reference_curation.md").read_text(encoding="utf-8")
    quickstart = Path("specs/017-learning-reference-curation/quickstart.md").read_text(encoding="utf-8")
    handoff = Path("docs/classical_sources/new_material_learning_handoff.md").read_text(encoding="utf-8")

    for marker in (
        "Authorization Audit Packet",
        "`authorization-status=ready_for_explicit_downstream_authorization`",
        "`downstream-mutation-authorized=false`",
        "`017-notes-closed=14`",
        "`017-next-action-ids=0`",
        "`012-boundary-leakage=0`",
        "`next-downstream-entry=013-explicit-candidate-review-or-015-queue-refresh`",
    ):
        assert marker in markdown
        assert marker in overview
        assert marker in quickstart
        assert marker in handoff
```

- [x] **Step 3: Run both tests and confirm RED**

```powershell
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py::test_learning_reference_authorization_audit_confirms_local_boundary_clearance tests/unit/test_learning_reference_curation.py::test_learning_reference_authorization_audit_markdown_and_docs_are_in_sync -q
```

Expected: FAIL because the builder and renderer do not exist yet.

### Task 2: Implement the Read-Only Audit Packet

**Files:**
- Modify: `src/mingli_engine/models.py`
- Modify: `src/mingli_engine/learning_reference_curation.py`

- [x] **Step 1: Add `LearningReferenceAuthorizationAudit`**

Add a frozen dataclass near `LearningReferenceProgressSummary` with fields:

```python
@dataclass(frozen=True)
class LearningReferenceAuthorizationAudit:
    audit_id: str
    authorization_status: str
    downstream_mutation_authorized: bool
    note_counts: dict[str, int]
    decision_counts: dict[str, int]
    candidate_status_counts: dict[str, int]
    review_decision_counts: dict[str, int]
    promotion_review_status_counts: dict[str, int]
    formal_evidence_unit_count: int
    formal_evidence_delta: int
    leakage_counts: dict[str, int]
    clearance_checks: dict[str, str]
    next_action_ids: list[str] = field(default_factory=list)
    next_downstream_entry: str = ""
    guardrails: list[str] = field(default_factory=list)
```

- [x] **Step 2: Build the audit from existing loaders**

Implement `build_learning_reference_authorization_audit()` in `learning_reference_curation.py`. It must compute counts from `build_learning_reference_progress_summary`, `load_candidate_intake_decisions`, `source_intake.load_candidate_extracts`, `source_intake.load_review_decisions`, `source_intake.load_promotion_batches`, and `classical_sources.load_evidence_units`.

- [x] **Step 3: Render a stable Markdown packet**

Implement `render_learning_reference_authorization_audit_markdown()` with the markers required by the tests and explicit guardrails that no downstream mutation is authorized by the audit itself.

### Task 3: Sync Maintainer Docs

**Files:**
- Modify: `docs/classical_sources/learning_reference_curation.md`
- Modify: `specs/017-learning-reference-curation/quickstart.md`
- Modify: `docs/classical_sources/new_material_learning_handoff.md`

- [x] **Step 1: Add Authorization Audit Packet markers**

Each document must include:

```text
Authorization Audit Packet
authorization-status=ready_for_explicit_downstream_authorization
downstream-mutation-authorized=false
017-notes-closed=14
017-next-action-ids=0
012-boundary-leakage=0
next-downstream-entry=013-explicit-candidate-review-or-015-queue-refresh
```

- [x] **Step 2: Update next long goal**

After this audit, the next long goal is `next-downstream-entry=013-explicit-candidate-review-or-015-queue-refresh`: either explicitly authorize 013 candidate/review work, or refresh the 015 queue for brand-new material reading.

### Task 4: Verify and Commit

**Files:**
- Verify all modified files.

- [x] **Step 1: Run focused tests**

```powershell
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest tests/unit/test_learning_reference_curation.py -q
```

- [x] **Step 2: Run audit smoke command**

```powershell
$env:PYTHONPATH='src'; uv run python -c "from mingli_engine.learning_reference_curation import build_learning_reference_authorization_audit, render_learning_reference_authorization_audit_markdown; audit=build_learning_reference_authorization_audit(); print(audit.authorization_status); print(audit.clearance_checks); print(render_learning_reference_authorization_audit_markdown(audit))"
```

- [x] **Step 3: Run full verification**

```powershell
git diff --check
$env:PYTHONPATH='src'; uv run --with pytest python -m pytest -q
```

- [x] **Step 4: Commit locally**

```powershell
git add docs/superpowers/plans/2026-06-27-learning-reference-authorization-audit.md src/mingli_engine/models.py src/mingli_engine/learning_reference_curation.py tests/unit/test_learning_reference_curation.py docs/classical_sources/learning_reference_curation.md specs/017-learning-reference-curation/quickstart.md docs/classical_sources/new_material_learning_handoff.md
git commit -m "feat: add learning reference authorization audit"
```
