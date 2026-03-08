# Paper Report Agent

`Paper Report Agent` 是一个面向单篇科研论文 PDF 的阅读与写作工作流仓库。

当前默认工作流是面向高上下文模型优化过的 `compact` 模式：不再把理解过程拆成过多独立阶段，而是先做一次完整分析，再写报告，最后审校修订。原始 7-stage 方案仍然保留为 `legacy`，用于对比或兼容旧习惯。

从 `v2.1` 开始，`run_pipeline.py` 会在每次启动时先清空 `workspace/intermediate/` 中上一次运行留下的中间产物，只保留目录占位文件。这是默认行为，目的是避免旧的中间状态污染新一轮论文分析。

## 为什么默认改成 `compact`

这个仓库最初把论文阅读拆成 `parse -> claims -> method -> experiments -> compare -> report -> review` 七次独立调用。这个思路对弱模型有帮助，但对像 Codex CLI 这种本身上下文能力较强的模型，常见副作用是：

- 每个阶段都在重复读论文和重复压缩信息
- 方法、实验、比较被拆散后，跨章节推理容易在阶段边界丢失
- 最终 `report` 阶段更像“改写中间摘要”，而不是“基于论文证据直接成文”
- 中间 JSON 和 notes 的写法会反过来污染最终报告表达

因此默认流程改成：

1. `analyze`：一次性读论文，产出高信号 `evidence_pack.md` 和完整 `extraction.json`
2. `report`：基于证据包写报告，并对关键结论回看 PDF
3. `review`：做一次 critic / revise，直接修订最终报告

## 设计原则

- 忠于原文优先，缺失就明确写“不确定”
- 尽量把“理解”集中在一次完整阅读里完成，而不是跨多个窄阶段反复压缩
- 中间产物只保留真正能服务下游写作的“证据态”，避免重复摘要
- `Main Technology / 主要技术` 必须是最深的部分之一
- 实验是支撑方法判断的证据，不是全文主体
- 关键数值转成可编辑 Markdown 表格
- 最终报告默认用自然中文，不保留机械化证据标签

## 默认工作流：`compact`

| Stage | Key | 主要目标 | 主要输出 |
|---|---|---|---|
| 1 | `analyze` | 一次性完成论文理解，建立证据包和结构化抽取 | `workspace/intermediate/evidence_pack.md` + `workspace/intermediate/extraction.json` |
| 2 | `report` | 基于证据包和 PDF 生成最终报告 | `workspace/output/final_report.md` |
| 3 | `review` | 审校报告并直接修订 | `workspace/intermediate/review_notes.md` + `workspace/output/final_report.md` |

### `analyze`

读取：

- `prompts/compact/01_analyze_paper.md`
- `templates/evidence_pack_template.md`
- `templates/extraction_template.json`

这一阶段是主理解阶段。要求一次性把以下内容连起来：

- 论文结构和关键信息位置
- 动机、问题设定、贡献
- 方法 pipeline、模块、训练、推理、部署
- 实验设置、主结果、消融、定性证据
- 比较、局限性、未来工作
- 所有重要不确定点

输出不是“漂亮摘要”，而是后续写作可直接依赖的 `evidence_pack.md`。

### `report`

读取：

- `prompts/compact/02_write_report.md`
- `workspace/intermediate/evidence_pack.md`
- `workspace/intermediate/extraction.json`
- `templates/report_template.md`
- `configs/report_schema.md`
- `configs/style_guide.md`

这一步把证据包改写成自然、严谨、技术细节充分的最终报告。`extraction.json` 只作为结构索引，不应反客为主地支配成文语气。

### `review`

读取：

- `prompts/compact/03_review_and_revise.md`
- `workspace/intermediate/evidence_pack.md`
- `workspace/intermediate/extraction.json`
- `workspace/output/final_report.md`
- `configs/quality_checklist.md`
- `configs/quality_rubric.md`

重点检查：

- 是否忠于论文
- 方法解释是否具体且完整
- 实验结论是否真的有表格/图支撑
- 是否有幻觉、越界推断或错误图表编号
- 最终报告是否仍然残留机械标签

## 兼容工作流：`legacy`

如果你仍然想使用最初的细粒度 7-stage 方案，可以显式指定：

```bash
python3 scripts/run_pipeline.py \
  --workflow legacy \
  --pdf workspace/input/Q-vla.pdf \
  --full-auto
```

`legacy` 保留原有阶段：

- `parse`
- `claims`
- `method`
- `experiments`
- `compare`
- `report`
- `review`

这个模式更适合调试单个局部环节，但默认不再推荐作为主路径。

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
│   ├── compact/
│   │   ├── 01_analyze_paper.md
│   │   ├── 02_write_report.md
│   │   └── 03_review_and_revise.md
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
│   ├── evidence_pack_template.md
│   ├── extraction_template.json
│   └── report_template.md
└── workspace/
    ├── input/
    ├── intermediate/
    ├── logs/
    └── output/
```

各目录职责：

- `AGENT.md`：全局规则
- `prompts/compact/`：默认的少阶段工作流 prompt
- `prompts/*.md`：原始 `legacy` 工作流 prompt
- `configs/`：报告结构、风格和质检要求
- `templates/`：结构化中间产物和最终报告骨架
- `scripts/run_pipeline.py`：workflow orchestrator
- `workspace/`：输入、输出、中间产物和运行日志

## 推荐运行方式

### 1. 准备输入论文

把待分析论文放到：

- `workspace/input/<paper>.pdf`

建议一次只放一篇。

### 2. 运行默认 `compact` 工作流

```bash
python3 scripts/run_pipeline.py \
  --pdf workspace/input/Q-vla.pdf \
  --full-auto
```

### 3. 只跑默认工作流的前半段

例如只跑到 `report`，不做最终审校：

```bash
python3 scripts/run_pipeline.py \
  --pdf workspace/input/Q-vla.pdf \
  --to-stage report \
  --full-auto
```

由于每次运行都会清空 `workspace/intermediate/`，当前内置 workflow 必须从首阶段启动：

- `compact` 必须从 `analyze` 开始
- `legacy` 必须从 `parse` 开始

### 4. 切回 `legacy` 工作流

```bash
python3 scripts/run_pipeline.py \
  --workflow legacy \
  --pdf workspace/input/Q-vla.pdf \
  --to-stage method \
  --full-auto
```

### 5. 只生成 prompt，不真正调用 Codex

```bash
python3 scripts/run_pipeline.py \
  --pdf workspace/input/Q-vla.pdf \
  --dry-run
```

## `run_pipeline.py` 做了什么

这个脚本是一个最小可用 orchestrator。它会：

1. 检查仓库布局和输入 PDF。
2. 根据 `--workflow`、`--from-stage`、`--to-stage` 选择阶段区间。
3. 在运行开始时清空 `workspace/intermediate/` 中上一次的中间产物。
4. 在需要时初始化 `workspace/intermediate/extraction.json`。
5. 为每个 stage 单独构造 prompt，并启动一次 `codex exec`。
6. 验证阶段输出是否存在、是否为空、JSON 是否合法。
7. 记录 manifest、stage prompt、stdout log 和最后一条 agent 回复。
8. 从各阶段日志里解析 `tokens used` 并汇总。

无论是 `compact` 还是 `legacy`，本质上都还是“多次独立调用 + 文件接力”。区别在于：

- `compact` 只让模型在少数高价值边界上切换上下文
- `legacy` 会把理解过程拆得更细

## 常用参数

| 参数 | 作用 |
|---|---|
| `--pdf` | 输入 PDF 路径 |
| `--workflow` | 选择 `compact` 或 `legacy` |
| `--from-stage` / `--to-stage` | 指定起止阶段；由于每次运行会清空 `workspace/intermediate/`，当前内置 workflow 只能从首阶段开始，`--to-stage` 仍可用于提前结束 |
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

默认 `compact` 模式的主要产物：

- `workspace/intermediate/evidence_pack.md`
- `workspace/intermediate/extraction.json`
- `workspace/intermediate/review_notes.md`
- `workspace/output/final_report.md`

`legacy` 模式还会额外使用：

- `workspace/intermediate/parsed_notes.md`
- `workspace/intermediate/method_notes.md`
- `workspace/intermediate/experiment_notes.md`

每次运行都会生成：

- `workspace/logs/run-YYYYMMDD-HHMMSS/`

同时会清空：

- `workspace/intermediate/` 中除 `.gitkeep` 以外的旧文件和旧目录

其中通常包含：

- `manifest.json`
- `<stage>.prompt.txt`
- `<stage>.stdout.log`
- `<stage>.last_message.txt`
- `token_usage.json`

## 一份好报告至少应满足

- 顶层结构完整，覆盖基本信息、动机、问题设定、贡献、技术、实验、比较、局限性、未来工作、总结
- `主要技术` 是全文最详细的部分之一
- 方法 pipeline 能按步骤复述，而不是只复述 abstract
- 关键术语、缩写和 paper-specific object 首次出现时被解释
- 至少包含一个可编辑 Markdown 结果表
- 引用原始 Figure / Table 编号，但不重绘图片
- 区分事实、证据和谨慎推断
- 明确写出不确定性，而不是编造缺失细节

## 建议的使用习惯

- 默认优先跑 `compact`
- 如果你想保留某次运行的中间产物，请在下次执行前自行复制出去；重新运行会先清空 `workspace/intermediate/`
- 如果怀疑方法部分不够深，优先回看 `evidence_pack.md`，而不是继续堆更多中间 notes
- 对机器人、VLA、LLM 论文，先检查方法 pipeline、训练、推理、部署是否真正讲清
- `review` 阶段不要省，它对降低幻觉和清理机械表达仍然很有价值
- 只有在你明确想调试某一个子问题时，再切到 `legacy`

## 当前版本的边界

- 依赖外部 `codex` CLI 和登录状态
- 没有更细粒度的自动质检脚本，只做了阶段级校验
- `extraction.json` 的校验仍然是顶层 schema 级别，不是字段级 validator
- 还没有专门为跨论文批处理、检索增强和综述写作设计
