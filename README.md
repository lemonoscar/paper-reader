# Paper Report Agent

`Paper Report Agent` 是一个面向单篇科研论文 PDF 的 7-stage 阅读与写作工作流。  
它的目标不是产出泛泛摘要，而是把一篇论文拆成可核查的中间证据，再生成一份结构化、技术细节充分、默认使用中文撰写的阅读报告。

## 这个仓库解决什么问题

读论文时，最常见的失败模式不是“没看摘要”，而是：

- 方法部分讲不清完整 pipeline，只会复述 abstract
- 实验部分堆很多表，却没有说清楚哪些结果真正支持了作者的主张
- 报告里混入编造的图表编号、数值或过度推断
- 最终成文可读性差，像把原文句子和标签硬拼起来

这个仓库用一个显式的 7-stage pipeline 来约束智能体：

1. 先建立论文结构索引和证据地图。
2. 再分阶段抽取事实、方法、实验和局限性。
3. 最后统一写成报告，并做一次 review/revise。

这使它更像一个“论文阅读工作流”，而不是一个单轮问答 prompt。

## 设计原则

- 忠于原文优先，缺失就明确写“不确定”
- 方法解释优先，尤其强调 system / model pipeline、训练、推理和部署链路
- 实验是证据，不是全文主体
- 关键定量结果转成可编辑 Markdown 表格
- 重要专有名词和缩写在首次出现时解释清楚
- 最终报告应当是自然中文，不要被机械的“作者明确表述”前缀破坏可读性

## 7-Stage 工作流

| Stage | Key | 主要目标 | 主要输出 |
|---|---|---|---|
| 1 | `parse` | 解析 PDF 结构，建立章节、图表和证据索引 | `workspace/intermediate/parsed_notes.md` |
| 2 | `claims` | 抽取动机、问题设定、贡献等核心事实 | `workspace/intermediate/extraction.json` |
| 3 | `method` | 深挖主要技术，重建端到端 pipeline，解释关键术语 | `workspace/intermediate/method_notes.md` + `workspace/intermediate/extraction.json` |
| 4 | `experiments` | 抽取数据集、指标、主结果、消融和关键表格 | `workspace/intermediate/experiment_notes.md` + `workspace/intermediate/extraction.json` |
| 5 | `compare` | 补全比较、局限性与未来工作 | `workspace/intermediate/extraction.json` |
| 6 | `report` | 基于模板和结构化抽取生成完整报告 | `workspace/output/final_report.md` |
| 7 | `review` | 审查幻觉、越界推断、图表引用和表达质量，再直接修订报告 | `workspace/intermediate/review_notes.md` + `workspace/output/final_report.md` |

### Stage 1: `parse`

读取 `prompts/01_parse_and_index.md`，目标是：

- 识别论文题目、作者、版本或 venue/year
- 重建章节结构
- 列出图表及其原始编号
- 标出动机、方法、实验、相关工作、局限性可能位于哪些章节

这一阶段不追求成文质量，重点是给后续阶段提供“证据索引”。

### Stage 2: `claims`

读取 `prompts/02_extract_core_claims.md`，把论文的核心事实回填到 `workspace/intermediate/extraction.json`：

- `basic_info`
- `motivation`
- `problem_setting`
- `contributions`

这一阶段仍然偏事实抽取，不提前写成漂亮 prose。

### Stage 3: `method`

读取 `prompts/03_extract_main_technology.md`。这是整条 pipeline 中最重要的一步。

要求不仅是“讲方法”，而是：

- 说清输入 / 输出
- 把完整 pipeline 按步骤拆开
- 解释核心模块的输入、输出、作用和连接关系
- 说明训练目标、推理流程和部署闭环
- 解释关键专有名词
- 判断真正的新意和最可能的性能来源

输出会写入：

- `workspace/intermediate/method_notes.md`
- `workspace/intermediate/extraction.json` 的 `main_technology` 段

### Stage 4: `experiments`

读取 `prompts/04_extract_experiments.md`，重点抽：

- 数据集 / benchmark
- 指标
- 主结果
- 消融
- 泛化或定性结果
- 效率 / 部署证据（如果论文有）

关键数值会转成 Markdown 表格，便于后续直接引用。

### Stage 5: `compare`

读取 `prompts/05_compare_and_limitations.md`，补全：

- `comparison`
- `limitations`
- `future_work`

这里强调的是“谨慎比较”。  
默认只在论文自身 `related work` 和实验比较提供足够证据时才做结论，不把它扩展成完整文献综述。

### Stage 6: `report`

读取：

- `prompts/06_write_report.md`
- `templates/report_template.md`
- `templates/extraction_template.json`
- `configs/report_schema.md`
- `configs/style_guide.md`

把前面各阶段积累的结构化信息统一写成：

- `workspace/output/final_report.md`

这一阶段会显式重写中间抽取结果，尽量避免把中间标签机械搬运到最终报告里。

### Stage 7: `review`

读取：

- `prompts/07_review_and_revise.md`
- `configs/quality_checklist.md`
- `configs/quality_rubric.md`

对最终报告做一轮 critic / self-revise，重点检查：

- 是否忠于论文
- 方法解释是否具体
- 实验证据是否真的出现
- 图表编号是否可靠
- 是否有幻觉或越界推断
- 局限性是否区分作者声明与谨慎推断

输出：

- `workspace/intermediate/review_notes.md`
- 修订后的 `workspace/output/final_report.md`

## 仓库结构

```text
.
├── AGENT.md
├── configs/
│   ├── quality_checklist.md
│   ├── quality_rubric.md
│   ├── report_schema.md
│   └── style_guide.md
├── prompts/
│   ├── 01_parse_and_index.md
│   ├── 02_extract_core_claims.md
│   ├── 03_extract_main_technology.md
│   ├── 04_extract_experiments.md
│   ├── 05_compare_and_limitations.md
│   ├── 06_write_report.md
│   └── 07_review_and_revise.md
├── scripts/
│   └── run_pipeline.py
├── templates/
│   ├── extraction_template.json
│   └── report_template.md
└── workspace/
    ├── input/
    ├── intermediate/
    ├── logs/
    └── output/
```

各目录职责可以这样理解：

- `AGENT.md`: 全局规则，定义智能体目标、语言和技术深度要求
- `prompts/`: 每个 stage 的局部任务说明
- `configs/`: 对最终报告的结构、风格和质检要求
- `templates/`: 最终报告和结构化抽取的骨架
- `scripts/run_pipeline.py`: 7-stage orchestrator
- `workspace/`: 本地运行目录，不是长期版本化内容

## 推荐运行方式

### 1. 准备输入论文

把待分析论文放到：

- `workspace/input/<paper>.pdf`

建议一次只放一篇，避免 agent 读错文件。

### 2. 直接运行完整 7-stage pipeline

```bash
python3 scripts/run_pipeline.py \
  --pdf workspace/input/Q-vla.pdf \
  --full-auto
```

### 3. 只跑部分阶段

例如从 `claims` 跑到 `review`：

```bash
python3 scripts/run_pipeline.py \
  --pdf workspace/input/Q-vla.pdf \
  --from-stage claims \
  --to-stage review \
  --full-auto
```

### 4. 只生成本次 prompt，不真正调用 Codex

```bash
python3 scripts/run_pipeline.py \
  --pdf workspace/input/Q-vla.pdf \
  --dry-run
```

## `run_pipeline.py` 做了什么

这个脚本不是“大而全”的 workflow engine，而是一个最小可用 orchestrator。它会：

1. 检查仓库布局和输入 PDF。
2. 根据 `--from-stage` / `--to-stage` 选择阶段区间。
3. 在需要时自动初始化 `workspace/intermediate/extraction.json`。
4. 为每个 stage 单独构造 prompt，并启动一次 `codex exec`。
5. 验证阶段输出是否存在、是否为空、JSON 是否合法。
6. 记录 manifest、stage prompt、stdout log 和最后一条 agent 回复。
7. 从每个 stage 的 stdout log 里解析 `tokens used`，汇总整条 pipeline 的 token 使用量。

这意味着整条 pipeline 不是“一段长对话”，而是“7 次独立的 Codex 调用，通过文件状态接力”。

## 常用参数

| 参数 | 作用 |
|---|---|
| `--pdf` | 输入 PDF 路径 |
| `--from-stage` / `--to-stage` | 指定起止阶段 |
| `--model` | 透传给 `codex exec` 的模型名 |
| `--profile` | 透传给 `codex exec` 的 profile |
| `--sandbox` | Codex sandbox 模式，默认 `workspace-write` |
| `--full-auto` | 让 `codex exec` 尽量自主执行 |
| `--search` | 启用 Codex search |
| `--ephemeral` | 不保留 Codex session 文件 |
| `--force-init-extraction` | 强制用模板覆盖 `workspace/intermediate/extraction.json` |
| `--dry-run` | 只生成运行提示和日志占位，不实际调用 Codex |
| `--codex-arg` | 透传额外原始参数给 `codex exec` |

## 运行产物

### 中间产物

- `workspace/intermediate/parsed_notes.md`
- `workspace/intermediate/extraction.json`
- `workspace/intermediate/method_notes.md`
- `workspace/intermediate/experiment_notes.md`
- `workspace/intermediate/review_notes.md`

### 最终产物

- `workspace/output/final_report.md`

### 每次运行的日志目录

- `workspace/logs/run-YYYYMMDD-HHMMSS/`

典型内容包括：

- `manifest.json`: 本次运行的参数快照
- `01_parse.prompt.txt`: 该阶段真正送给 Codex 的 prompt
- `01_parse.stdout.log`: 该阶段的完整 CLI 输出
- `01_parse.last_message.txt`: 阶段结束时 agent 的收尾回复
- `token_usage.json`: 各阶段及总 token 统计

## 最终报告应该长什么样

一份合格的 `final_report.md` 至少应满足：

- 顶层结构完整，覆盖基本信息、动机、问题设定、贡献、技术、实验、比较、局限性、未来工作、总结
- `Main Technology / 主要技术` 是全文最详细的部分之一
- 可以把方法的 pipeline 按步骤复述出来，而不是只复述 abstract
- 关键术语、缩写和 paper-specific object 在首次出现时有简洁解释
- 至少包含一个可编辑 Markdown 结果表
- 引用原始 Figure / Table 编号，但不重绘图片
- 区分事实、证据和谨慎推断
- 明确写出不确定性，而不是编造缺失细节

## 建议的使用习惯

- 优先按 stage 跑，不要一开始就追求“一条指令跑到底”
- `method` 阶段完成后先人工抽查一遍，再决定是否继续
- 对机器人、VLA、LLM 论文，优先看方法 pipeline 是否真正讲清
- 实验部分优先保留主结果、关键消融和部署证据，不要机械抄全表
- `review` 阶段不要省，它对减少幻觉和改善成文质量很有用

## 什么适合进版本库，什么不适合

当前仓库默认只版本化“流程定义”本身：

- 适合上传：`AGENT.md`、`prompts/`、`configs/`、`templates/`、`scripts/`、`README.md`
- 不适合上传：输入 PDF、运行日志、中间产物、最终报告

因此 `.gitignore` 默认忽略：

- `workspace/input/*`
- `workspace/intermediate/*`
- `workspace/output/*`
- `workspace/logs/*`
- Python `__pycache__` 和本地环境目录

`workspace/` 目录里只保留空目录占位文件，方便新环境直接运行。

## 当前版本的边界

这是一个工程上可用、但仍然偏轻量的 workflow 定义仓库，而不是重型调度系统。它当前的边界包括：

- 依赖外部 `codex` CLI 和登录状态
- 没有更细粒度的自动质检脚本，只做了阶段级基本校验
- 结构化抽取仍然以模板和 prompt 约束为主，没有更强的 schema validator
- 对跨论文批处理、检索增强和多篇综述写作没有专门设计

## 后续可以继续增强的方向

- 给 `final_report.md` 增加更严格的结构检查
- 增加对 `extraction.json` 更细的字段级校验
- 统一历史命名，去掉 `method_notes.md` / `methods_notes.md` 这种重复痕迹
- 增加样例 run 和回归测试数据
- 在更强模型下重新评估阶段拆分粒度，减少不必要的信息搬运
