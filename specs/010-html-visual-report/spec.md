# Feature Specification: HTML 可视化报告

**Feature Branch**: `010-html-visual-report`

**Created**: 2026-05-23

**Status**: Draft

**Input**: User description: "010 HTML 可视化报告：给现有安全正式报告增加纯静态 HTML 输出。现有 `calculate-report` 和 `generate-report` 命令应支持 `--format html`，输出单页阅读版、无 JavaScript、无外部资源的完整 HTML 文档。复用当前 Report 内容，不新增命理判断、不改算法、不改输入；红线请求和无效输入仍返回原有 JSON 或错误行为。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 用户能直接生成 HTML 报告 (Priority: P1)

作为使用命令行生成命理报告的人，我希望在现有报告命令里选择 `--format html`，得到一份完整、可保存、可打印的 HTML 报告，而不是只能得到 Markdown。

**Why this priority**: 010 的核心价值是把现有安全报告增加一个更适合阅读和后续导出的展示格式。只要安全输入能通过现有命令输出 HTML，就能形成可交付的 MVP。

**Independent Test**: 使用安全自动排盘输入运行 `calculate-report --format html`，检查命令成功返回完整 HTML 文档，并且文档包含正式报告的标题、免责声明、快速导读、四层结构、术语简注和伦理提醒。

**Acceptance Scenarios**:

1. **Given** 一个安全完整的自动排盘出生资料输入，**When** 用户运行 `calculate-report --format html`，**Then** 系统输出以 `<!doctype html>` 开始的完整 HTML 报告。
2. **Given** 一个安全完整的外部核对盘输入，**When** 用户运行 `generate-report --format html`，**Then** 系统输出同样完整的 HTML 报告。
3. **Given** 用户继续使用 `--format markdown`，**When** 用户运行现有报告命令，**Then** Markdown 输出保持可用且不被 HTML 功能改变。

---

### User Story 2 - 读者能按原报告顺序阅读 HTML (Priority: P2)

作为阅读报告的人，我希望 HTML 报告保留现有 Markdown 报告的阅读顺序和层级，这样我不会因为换了输出格式而误解内容。

**Why this priority**: HTML 是展示层，不应该改变报告含义。保留现有顺序能确保 004-009 已经建立的阅读路径、边界说明和观察依据继续有效。

**Independent Test**: 生成一份安全 HTML 报告，检查主要内容按标题、免责声明、快速导读、第一层基础资料、第二层结构观察、观察依据、第三层解读边界、第四层行动反思、术语简注、伦理提醒的顺序出现。

**Acceptance Scenarios**:

1. **Given** 一份安全 HTML 报告，**When** 读者从上到下阅读，**Then** 看到的主要章节顺序与当前 Markdown 报告一致。
2. **Given** HTML 报告包含结构观察层，**When** 读者查看该层，**Then** `观察依据` 仍位于十神摘要之后、结构分析之前。
3. **Given** HTML 报告包含来源说明，**When** 读者查看基础资料层，**Then** 自动排盘或外部核对盘来源不被误标。

---

### User Story 3 - 维护者能守住 HTML 安全边界 (Priority: P3)

作为维护报告生成器的人，我希望 HTML 输出不会引入脚本、外部资源、HTML 注入或新的命理断语，这样展示层不会削弱原有安全边界。

**Why this priority**: HTML 输出会接触浏览器和保存场景，必须保证报告文字被安全转义，并且红线请求仍不生成正式报告。

**Independent Test**: 使用包含 HTML 特殊字符的报告内容构造安全报告，检查输出会转义这些字符；使用红线输入请求 HTML 报告，检查系统仍返回安全 JSON 而不是 HTML。

**Acceptance Scenarios**:

1. **Given** 报告字段里包含 `<`, `>`, `&` 或引号等字符，**When** 系统渲染 HTML，**Then** 这些字符不会破坏 HTML 结构。
2. **Given** 用户请求寿命、死亡时间等红线主题，**When** 用户运行报告命令并选择 `--format html`，**Then** 系统继续返回安全 JSON，不输出正式 HTML 报告。
3. **Given** 一份安全 HTML 报告，**When** 维护者检查输出，**Then** 不出现 `<script>`、外部资源链接、事件处理属性或绝对化命运语言。

---

### Edge Cases

- 安全自动排盘报告和安全外部核对盘报告都必须支持 HTML 输出。
- 红线主题请求 `--format html` 时仍必须返回安全 JSON，不得为了展示 HTML 而绕过拒绝流程。
- 缺少必要出生资料或输入 JSON 形状错误时，错误行为必须保持与现有命令一致。
- HTML 输出必须转义用户输入、来源说明、关注主题和其他报告文本里的 HTML 特殊字符。
- HTML 输出不得引用外部字体、图片、脚本、样式表或 CDN。
- HTML 输出不得添加新的命理结论、图表、仪表盘、交互控件或 Web 输入表单。
- Markdown 输出必须保持现有行为，不得因为新增 HTML 格式而改变章节顺序或文本边界。
- HTML 报告应适合保存和打印，但 010 不要求实现 PDF 或 PNG 导出。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `calculate-report` MUST accept `--format html` for safe complete birth-profile inputs.
- **FR-002**: `generate-report` MUST accept `--format html` for safe complete chart inputs.
- **FR-003**: Safe HTML report output MUST be a complete standalone HTML document with document type, language, charset metadata, title, inline style, and one main report body.
- **FR-004**: HTML output MUST preserve the same report content and major reading order as the current formal Markdown report.
- **FR-005**: HTML output MUST include the existing disclaimer, quick guide, chart card, source assumptions, four-pillar summary, five-element summary, ten-god summary, observation basis, structure analysis, personality tendencies, interpretation boundaries, strengths and issues, phase overview, action suggestions, glossary, and ethics reminder.
- **FR-006**: HTML output MUST keep `观察依据` inside the structure-observation layer after ten-god summary and before structure analysis.
- **FR-007**: HTML output MUST use semantic headings and sections so the report can be read without relying on visual styling alone.
- **FR-008**: HTML output MUST include inline CSS only and MUST NOT require JavaScript, external stylesheets, external fonts, images, or network resources.
- **FR-009**: HTML rendering MUST escape report text so user-supplied or source-provided content cannot inject markup, scripts, or attributes.
- **FR-010**: Existing `--format markdown` behavior MUST remain available and unchanged for both report commands.
- **FR-011**: Unsafe red-line requests with `--format html` MUST continue returning safety JSON instead of a formal HTML report.
- **FR-012**: Invalid inputs with `--format html` MUST continue using the existing invalid-input or clarification behavior instead of generating partial HTML.
- **FR-013**: The feature MUST NOT add new CLI commands, user input fields, chart calculations, interpretation conclusions, Web forms, interactive controls, dashboards, PDF export, or PNG export.
- **FR-014**: Automated validation MUST cover safe automatic-chart HTML output, safe external-verified HTML output, unsafe red-line HTML requests, and HTML escaping.

### Safety & Ethics Requirements *(mandatory for domain features)*

- **SE-001**: System MUST present outputs as cultural interpretation and self-reflection, not scientific prediction or fate verdict.
- **SE-002**: System MUST refuse or safely redirect requests involving lifespan, death timing, major disaster prediction, deterministic marriage matching, medical advice, legal advice, psychological treatment, investment instruction, unauthorized third-party full-chart analysis, anxiety creation, or paid remedy upsells.
- **SE-003**: System MUST include a disclaimer in every formal report.
- **SE-004**: System MUST avoid absolute destiny language such as 必定, 注定, 一定会, 死定, or equivalent phrasing.
- **SE-005**: System MUST expose chart data source and key calculation assumptions where reports depend on calendrical or school-specific rules.
- **SE-006**: HTML presentation MUST NOT make the report appear more deterministic, predictive, authoritative, or professional-advice-like than the Markdown report.
- **SE-007**: HTML output MUST protect browser-facing readers from markup injection by escaping all report text.

### Key Entities *(include if feature involves data)*

- **HTML 报告**: 从现有安全 `Report` 内容渲染出的完整静态 HTML 文档，用于阅读、保存和打印。
- **HTML 渲染器**: 只负责把 `Report` 转成 HTML 展示层的组件，不负责排盘、解释、红线判断或输入校验。
- **报告格式选项**: 现有报告命令的输出格式选择，010 后包含 `markdown` 和 `html`。
- **安全拒绝结果**: 红线请求返回的 JSON 结果；即使用户请求 HTML，也不能生成正式 HTML 报告。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of safe `calculate-report --format html` runs with supported complete inputs return a complete HTML report.
- **SC-002**: 100% of safe `generate-report --format html` runs with supported complete chart inputs return a complete HTML report.
- **SC-003**: 100% of HTML report regression checks verify that the report contains the required major sections in the required order.
- **SC-004**: 100% of HTML escaping checks verify that `<`, `>`, `&`, and quote characters in report text do not appear as executable or structural markup.
- **SC-005**: 100% of unsafe red-line report requests with `--format html` continue returning safety JSON instead of `<!doctype html>`.
- **SC-006**: 0 new user-facing commands, input fields, chart calculations, interpretation conclusions, JavaScript interactions, external assets, PDF exports, or PNG exports are required for 010.
- **SC-007**: 100% of existing Markdown report tests continue passing after HTML output is added.

## Assumptions

- The first HTML version should prioritize stable reading, saving, and printing over visual complexity.
- A pure static single-page report is sufficient for 010; Web input and preview can be a later feature.
- Existing `Report` fields contain all content needed for the first HTML report.
- Existing safety checks and report-building flow remain the authority for whether a formal report may be generated.
- Visual styling can be tested through structural HTML assertions rather than browser screenshot snapshots in 010.
