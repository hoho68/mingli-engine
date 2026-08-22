# OpenCode 新增资料学习执行交接计划

## 一、执行目标

在 OpenCode 1.18.15 中执行已批准的新增资料学习设计和详细实现计划：

- 设计：`docs/superpowers/specs/2026-08-08-new-material-learning-restart-design.md`
- 主计划：`docs/superpowers/plans/2026-08-08-new-material-learning-restart.md`
- 输入：`E:\_mingli-new-material-intake\2026.07.14新增资料`
- 基线：29 个非视频文件，其中 28 个 PDF、1 个 DOCX，总计 1,255,999,661 字节。
- 旧任务：停止继续学习 `资料原文`，保留已经验证并进入知识库的成果。
- 视频：完全忽略；不读取、不复制、不转录、不建立学习任务、不计入完成率。

OpenCode 必须在 `E:\命理演绎` 中执行，并遵守根目录 `AGENTS.md` 以及其引用的
`specs/_drafts/019-bazi-domain-validation-and-application-v1/plan.md`。

## 二、模型绑定

| 工作类型 | OpenCode 模型 | 使用边界 |
|---|---|---|
| 批量纯文本分段、摘要、概念与候选规则抽取、初步聚类去重 | `deepseek/deepseek-chat` | 默认文本苦活模型；不得处理无可靠文本层的扫描页 |
| 少量复杂规则冲突、适用条件推理和疑难复核 | `deepseek/deepseek-reasoner` | 仅处理主审标记的疑难项，不做全量重复工作 |
| 扫描 PDF、图片页面、复杂版面、长上下文跨页理解 | `kimi-for-coding/k3-256k` | 仅在文本层不可靠或必须视觉理解时使用 |
| Kimi 备用 | `kimi-for-coding/k3` | `k3-256k` 不可用时使用；必须在运行记录中注明切换原因 |
| 编排、来源核验、正式晋升、回归测试和最终验收 | 当前 OpenCode 主代理 | 不得把模型草稿直接视为正式知识 |

禁止静默回退到 OpenAI、Kimi CLI 的 OAuth 默认模型或其他 provider。任何模型不可用时，相关文件进入
`blocked`，原因必须包含 provider、model 和失败阶段。

## 三、执行前门禁

### 3.1 检查 Git 与工作区

```powershell
Set-Location -LiteralPath 'E:\命理演绎'
git status --short --branch
git diff --check
```

预期只有以下两份已批准但未提交的设计/计划文档；不得覆盖或清理它们：

```text
docs/superpowers/specs/2026-08-08-new-material-learning-restart-design.md
docs/superpowers/plans/2026-08-08-new-material-learning-restart.md
```

Git 尚未配置提交者姓名和邮箱。不得配置身份，不得 commit、push、merge、reset 或删除工作树。每个阶段使用
`git diff --check`、`git status --short` 和测试结果作为检查点。

### 3.2 检查 provider 凭据与模型

```powershell
opencode providers list
opencode models deepseek
opencode models kimi-for-coding
```

必须满足：

- provider 列表中存在可用的 DeepSeek 凭据。
- provider 列表中存在可用的 Kimi for Coding 凭据。
- 模型清单包含 `deepseek/deepseek-chat`、`deepseek/deepseek-reasoner`、
  `kimi-for-coding/k3-256k` 和 `kimi-for-coding/k3`。

当前已知状态只有 OpenAI OAuth 凭据；因此首次执行前需要由用户在 OpenCode 中完成 DeepSeek 和 Kimi provider
登录或配置。不要读取、打印或提交密钥。任一 provider 未配置时停止，不开始正文处理。

### 3.3 验证项目基线

```powershell
uv sync --frozen
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest -q -p no:cacheprovider
```

完整测试必须在修改前通过。失败即停止并报告，不能把已有失败归因于新增资料。

## 四、启动 OpenCode

推荐用当前主代理进入项目：

```powershell
opencode 'E:\命理演绎'
```

进入后粘贴以下启动指令：

```text
读取并严格执行：
1. AGENTS.md
2. docs/superpowers/specs/2026-08-08-new-material-learning-restart-design.md
3. docs/superpowers/plans/2026-08-08-new-material-learning-restart.md
4. docs/superpowers/plans/2026-08-08-new-material-learning-opencode-handoff.md

按主计划 Task 1 到 Task 8 顺序执行。先验证 DeepSeek/Kimi provider 和完整测试基线。
视频完全忽略。原始资料不得进入 Git。旧资料原文任务保持冻结，已验证成果保留。
DeepSeek Chat 做批量纯文本任务，DeepSeek Reasoner 只做疑难冲突，Kimi K3-256k 只做多模态或长上下文任务。
所有模型输出均为候选，必须由主代理核验来源定位、条件、限制、风险、重复和冲突后才能晋升。
不得配置 Git 姓名邮箱，不得 commit、push、merge 或删除现有内容。
每完成一个 Task，更新计划复选框并输出文件数量、状态、测试结果和下一步。
遇到哈希变化、测试失败、provider 缺失、模型输出无法定位原文或正式知识冲突无法裁决时立即停止晋升并报告。
```

## 五、阶段执行与模型调度

### 阶段 A：清单与不可变基线

1. 只枚举输入目录的文件元数据。
2. 用固定视频扩展名集合排除视频；即使发现视频，也只增加 `excluded_video_count`，不读取文件内容。
3. 为每个非视频文件记录相对路径、扩展名、字节数和 SHA256。
4. 生成 `batch_20260714_manifest.json`，预期恰好 29 条。
5. 检测相同 SHA256；重复文件仍各有清单记录，但只建立一次内容处理任务。

门禁：29 条记录、28 PDF、1 DOCX；哈希完整；输入目录无写入。

### 阶段 B：文本能力探测与模型路由

1. 用 `pdfinfo`/`pdftotext` 检查 PDF 页数、非空文本页数和字符密度。
2. 用 Python 标准库 `zipfile` 与 XML 解析 DOCX 正文，不修改 DOCX。
3. 有可靠文本层的文件路由到 `deepseek/deepseek-chat`。
4. 无可靠文本层、扫描图像或复杂版面文件路由到 `kimi-for-coding/k3-256k`。
5. 加密、损坏或无法打开的文件标为 `blocked`，记录工具输出和恢复条件。

门禁：29 个文件全部得到 `deepseek_text`、`kimi_multimodal` 或 `blocked` 路由。

### 阶段 C：批量学习提炼

DeepSeek 每次只处理有明确页码/章节边界的文本块，输出严格 JSON：

```json
{
  "file_sha256": "64位SHA256",
  "source_locators": ["page:1-3"],
  "summary": "简洁摘要",
  "learning_points": [],
  "rule_candidates": [],
  "limitations": [],
  "risk_tier": "ordinary|sensitive|high_risk",
  "model_id": "deepseek/deepseek-chat",
  "prompt_version": "batch_20260714_v1"
}
```

Kimi 只处理需要视觉理解的指定页，不得无差别上传整个大文件。输出使用同一 JSON 结构，`model_id` 为
`kimi-for-coding/k3-256k`，定位必须包含页码，并区分“页面可见文字”和“模型推断”。

每个模型任务以 `file_sha256 + chunk/page range + prompt_version + model_id` 为缓存键。成功结果不重复调用；失败最多重试
两次，之后标为 `blocked` 或 `deferred`。

门禁：缺少来源定位、限制、模型标识、输入哈希或包含绝对化断言的输出全部拒收。

### 阶段 D：主代理复核与知识晋升

1. 主代理逐项核对候选与对应原文定位。
2. 与现有 017 学习点、013 候选和 012 正式证据做重复检查。
3. 重复内容标为 `duplicate`，保留新增来源关系，不重复创建规则。
4. 新旧冲突不覆盖旧知识；登记双方来源、流派、条件和证据强弱。
5. 无法裁决的冲突标为 `learned_not_promoted`。
6. 只有来源可追踪、条件与限制完整、语言安全、冲突已解决且测试通过的候选才自动晋升。
7. 晋升后写入现有 017/013/012 数据链，并保持历史记录不变。

门禁：每条正式知识都能追溯到输入哈希和页码/章节；模型草稿不能直接进入正式知识库。

### 阶段 E：文件终态与验收

每个非视频文件必须有且只有一个终态：

- `promoted`
- `learned_not_promoted`
- `duplicate`
- `blocked`
- `deferred`

`blocked`/`deferred` 允许批次关闭，但必须有明确原因、已完成步骤和恢复条件。状态总数必须等于29，不能存在
`pending`。

执行完整测试、学习质量检查、来源与证据验证以及输入重新哈希。验收报告保存到：

```text
docs/classical_sources/new_material_20260714_learning.md
```

报告必须包含：

- 29 文件对账及扩展名分布。
- 视频排除数及“视频未进入分母”的确认。
- DeepSeek/Kimi 路由和实际调用次数。
- 学习点、候选、复用、重复、冲突和晋升数量。
- 五种终态数量及阻塞/延期明细。
- 质量检查、完整测试、`git diff --check` 和最终 Git 状态。
- `资料原文` 未继续学习、旧验证成果未被删除或无证据覆盖的确认。

## 六、强制停止条件

出现以下任一情况立即停止当前晋升阶段并报告：

- 输入文件 SHA256 与清单不一致。
- 非视频文件数量不再是29且无法解释。
- DeepSeek/Kimi provider 或指定模型不可用。
- 模型输出缺少可复核原文定位。
- 模型输出包含无法纠正的虚构来源、绝对化命运判断或高风险建议。
- 新旧规则冲突无法可靠标注条件或流派。
- 任一质量检查、回归测试或 `git diff --check` 失败。
- 原始资料、视频或密钥出现在 Git 状态中。

## 七、最终验收命令

```powershell
Set-Location -LiteralPath 'E:\命理演绎'
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'

uv sync --frozen
uv run --frozen mingli-engine validate-new-material-learning --batch batch_20260714
uv run --frozen --with pytest==8.4.1 python -m pytest -q -p no:cacheprovider
git diff --check
git status --short --branch
```

完成声明必须引用这些命令的新鲜输出，不得只引用模型或子任务的成功报告。
