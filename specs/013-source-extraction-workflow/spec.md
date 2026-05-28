# Feature Specification: 资料抽取与证据增补流程

**Feature Branch**: `013-source-extraction-workflow`

**Created**: 2026-05-28

**Status**: Draft

**Input**: User description: "按审核队列优先方式推进 013：从用户提供的 PDF/Markdown 资料登记候选摘录，记录来源、摘录范围、审核状态、风险边界和冲突说明；只有审核通过的候选证据才能进入正式 classical evidence corpus。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 登记候选摘录 (Priority: P1)

资料整理者需要把用户提供的原始资料登记为候选摘录，而不是直接加入正式证据库。每条候选摘录都必须保留可追溯来源、摘录范围、候选规则分类、风险边界和初始审核状态，方便后续人工审核。

**Why this priority**: 这是整个流程的入口。没有可靠的候选登记，就无法保证后续证据增补可追溯、可复核，也无法保护根目录 PDF 和 `Markdown/` 这类用户资料不被误当作已审核证据。

**Independent Test**: 可以通过登记一条来自用户资料的候选摘录来验证；登记完成后，该候选项应处于待审核状态，并且不会出现在正式报告可用证据中。

**Acceptance Scenarios**:

1. **Given** 一份用户提供的原始资料和一个待整理段落，**When** 资料整理者登记候选摘录，**Then** 系统记录资料标识、来源定位、摘录摘要或短摘、候选规则分类、风险等级、整理说明和待审核状态。
2. **Given** 候选摘录缺少来源定位或资料标识，**When** 资料整理者尝试提交为待审核，**Then** 系统拒绝进入待审核队列并说明缺失项。
3. **Given** 候选摘录只是登记完成但尚未审核，**When** 正式报告或正式证据覆盖统计使用证据库，**Then** 该候选摘录不会被当作可用证据。

---

### User Story 2 - 审核并决定候选证据去向 (Priority: P2)

证据审核者需要逐条审阅候选摘录，决定批准、退回修改、拒绝或标记阻塞。批准项必须带有审核人、审核时间、审核结论、限制说明和入库批次，才能成为正式可用证据。

**Why this priority**: 审核队列的价值在于把原始资料和正式 evidence corpus 隔开。只有审核决策完整，才能避免未经复核、含混或高风险表述进入正式解释链。

**Independent Test**: 可以通过审核一条候选摘录验证；批准后应具备完整审核元数据并可进入正式证据增补清单，退回或拒绝项仍保持不可用。

**Acceptance Scenarios**:

1. **Given** 一条资料、定位、规则分类和风险等级完整的候选摘录，**When** 审核者批准它，**Then** 系统记录审核结论、审核说明、审核人、审核时间、限制说明和入库批次，并将其标记为可进入正式证据增补。
2. **Given** 一条候选摘录含有高风险或绝对化判断，**When** 审核者尝试批准但未填写风险限制说明，**Then** 系统阻止批准并要求补充限制说明。
3. **Given** 一条候选摘录被退回、拒绝或标记阻塞，**When** 正式 evidence corpus 生成或报告引用证据，**Then** 该摘录不得被引用为正式证据。

---

### User Story 3 - 记录冲突、缺口和拒绝理由 (Priority: P3)

证据审核者需要把候选摘录与既有 012 证据进行对照，记录重复、冲突、范围不清、来源不足、高风险不可用等情况。被拒绝或阻塞的候选项也要保留原因，以便后续回看资料覆盖情况。

**Why this priority**: 古籍/江湖资料常见口径差异和表述风险。记录冲突与缺口可以防止相互矛盾的说法静默入库，也让未纳入内容有清楚边界。

**Independent Test**: 可以用一条与既有证据口径不一致的候选摘录验证；审核结果应能记录冲突类型、涉及证据、处理状态和不可用原因。

**Acceptance Scenarios**:

1. **Given** 一条候选摘录与既有证据在同一规则分类下存在口径差异，**When** 审核者记录冲突，**Then** 系统保留冲突类型、严重程度、相关证据、审核说明和处理状态。
2. **Given** 一份资料暂时无法形成可安全改写的证据，**When** 审核者登记缺口，**Then** 系统记录缺口原因、影响范围和后续处理建议。
3. **Given** 一条候选摘录因为版权、来源不明或高风险表述被拒绝，**When** 后续查看资料整理进度，**Then** 拒绝原因仍可追溯。

---

### User Story 4 - 查看资料整理进度 (Priority: P4)

项目维护者需要看到候选摘录队列的阶段性进度，包括原始资料登记数量、待审核数量、已批准数量、退回/拒绝/阻塞数量、风险分布、规则分类覆盖和未处理缺口。

**Why this priority**: 013 需要分阶段推进。进度视图能帮助用户判断下一步是继续整理资料、处理高风险候选、补充冲突说明，还是把已批准项合入正式证据库。

**Independent Test**: 可以基于一组候选摘录和审核决策生成进度摘要；摘要应清楚区分候选、已批准、阻塞和正式可用证据。

**Acceptance Scenarios**:

1. **Given** 候选队列中存在多种审核状态，**When** 维护者查看进度摘要，**Then** 摘要按状态、资料来源、规则分类和风险等级展示数量。
2. **Given** 有候选项被批准但尚未合入正式证据库，**When** 维护者查看进度摘要，**Then** 摘要明确显示这些项目处于待入库状态。
3. **Given** 有资料尚未登记任何候选摘录，**When** 维护者查看进度摘要，**Then** 摘要显示该资料仍存在整理缺口。

### Edge Cases

- 原始资料存在但尚未转换或尚未阅读时，系统只能登记资料状态，不得生成候选证据。
- 候选摘录定位不稳定时，必须用可复核的章节、页码、文件名、段落标题或整理说明补足定位。
- 候选摘录与既有证据高度重复时，应标记为重复或合并建议，而不是制造重复证据。
- 候选摘录包含长篇原文时，正式记录必须改为短摘、摘要或释义，避免大段复制。
- 候选摘录涉及寿命、死亡、疾病、法律、投资、心理治疗或付费化解时，必须进入高风险审核路径。
- 候选摘录无法判断来源质量时，不得批准为正式证据。
- 已批准候选在入库前发现冲突或安全问题时，必须允许撤回批准或标记阻塞。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow maintainers to register source materials as review inputs without requiring those materials to become tracked project assets.
- **FR-002**: System MUST distinguish raw source materials, candidate extracts, approved evidence additions, rejected items, blocked items, and formal report-usable evidence.
- **FR-003**: System MUST require every candidate extract to include a source material identifier, source locator, extracted meaning, proposed rule family, risk tier, and initial review status before it can enter the review queue.
- **FR-004**: System MUST prevent any candidate extract that is not approved from being treated as formal report-usable evidence.
- **FR-005**: System MUST support review decisions of approved, returned for revision, rejected, and blocked, with reviewer, review date, rationale, and next-step notes.
- **FR-006**: System MUST require approved candidate extracts to include limitation notes, source quality assessment, confidence level, and curation batch reference before promotion to the formal evidence corpus.
- **FR-007**: System MUST require high-risk candidate extracts to include explicit uncertainty and limitation notes before they can be approved.
- **FR-008**: System MUST flag likely duplicate candidates when source material, locator, rule family, and extracted meaning overlap with existing candidates or formal evidence.
- **FR-009**: System MUST allow reviewers to link candidates to source conflicts, existing evidence, curation gaps, and rejection reasons.
- **FR-010**: System MUST preserve rejected and blocked candidate records for audit and coverage review instead of silently deleting them.
- **FR-011**: System MUST provide a progress summary that separates source material coverage, candidate queue status, approval readiness, risk distribution, rule-family coverage, conflicts, and gaps.
- **FR-012**: System MUST keep the formal report contract stable: reports may only consume evidence that has passed the approved evidence path, not raw materials or pending candidates.
- **FR-013**: System MUST make it possible to audit how an approved evidence addition moved from source material to candidate extract to reviewer decision to formal corpus entry.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MAY make substantive traditional 命理 judgments only after evidence has passed review and remains tied to chart data, source context, and confidence boundaries.
- **SE-002**: System MUST present curated material as traditional evidence analysis, not scientific proof, destiny enforcement, or guaranteed real-world outcomes.
- **SE-003**: System MUST include or preserve formal report disclaimers wherever approved evidence later influences generated reports.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing in candidate summaries, approved evidence, and report-facing notes.
- **SE-005**: System MUST expose source material, source locator, review decision, and evidence boundary where reports depend on curated classical evidence.
- **SE-006**: System MAY discuss traditionally high-risk signals when source-backed and reviewed, but MUST label uncertainty and MUST refuse guaranteed death timing, exact lifespan, medical diagnosis or treatment, legal instruction, psychological treatment, investment instruction, coercive matching, anxiety creation, and paid-remedy upsells.
- **SE-007**: System MUST avoid wholesale copying of source materials into candidate records, review notes, formal evidence, or reports.

### Key Entities *(include if feature involves data)*

- **Source Material**: A user-provided or project-recognized classical source input. Key attributes include material identifier, title or file label, material type, preparation status, review eligibility, and notes about whether it has usable candidate extracts.
- **Candidate Extract**: A proposed evidence item derived from a source material but not yet trusted. Key attributes include source locator, extracted meaning, candidate rule family, risk tier, proposed limitation, reviewer status, and links to related evidence or conflicts.
- **Review Decision**: A human review outcome for a candidate extract. Key attributes include decision, reviewer, review date, rationale, required changes, rejection reason, and approval limitations.
- **Promotion Batch**: A group of approved candidate extracts prepared for formal evidence corpus updates. Key attributes include batch identifier, included candidates, approval scope, and readiness status.
- **Conflict Or Gap Note**: A record explaining why candidate material disagrees with existing evidence, duplicates existing evidence, remains unsafe, or cannot yet be converted into formal evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of candidate extracts in the review queue include source material identifier, source locator, proposed rule family, risk tier, extracted meaning, and review status.
- **SC-002**: 0 unapproved candidate extracts are available to formal report generation or counted as formal report-usable evidence.
- **SC-003**: 100% of approved high-risk candidate extracts include explicit uncertainty and limitation notes before promotion.
- **SC-004**: Reviewers can identify pending, approved, rejected, blocked, duplicate, and gap-related candidate counts from a progress summary without manually inspecting every candidate.
- **SC-005**: 100% of approved evidence additions can be traced back to their source material, locator, reviewer decision, and promotion batch.
- **SC-006**: At least one rejected or blocked candidate can be preserved with a clear reason and excluded from formal evidence, demonstrating that non-approved material is auditable but not report-usable.

## Assumptions

- The primary users for 013 are project maintainers and evidence reviewers, not end users reading reports.
- Existing 012 classical evidence structures remain the formal evidence boundary; 013 creates a controlled intake path before evidence enters that boundary.
- User-provided root PDF files and the root `Markdown/` directory remain external preparation material unless the user explicitly asks to track, move, convert, or delete them.
- Manual human review is required for approval. Automation may assist with organization or detection, but it cannot approve evidence by itself.
- Candidate extraction stores source knowledge and review metadata only; it does not store personal birth data or generated user reports.
- The first implementation should prioritize traceability and safety over extraction volume.
