# Paper Report Agent

这是一个面向单篇科研论文 PDF 的智能体流水线骨架。它的目标不是生成泛泛摘要，而是把论文解析成一份结构化、可追溯、技术细节充分的中文阅读报告。

## 仓库审查结论

从当前仓库结构看，这个智能体的 pipeline 主要做的是：

1. 读取一篇输入论文 PDF。
2. 先做结构化解析，识别标题、作者、章节、图表编号。
3. 分阶段抽取论文事实，包括动机、问题设定、贡献、核心技术、实验结果、局限性和未来工作。
4. 基于模板写成一份 Markdown 报告。
5. 再做一轮自审，检查是否忠于原文、是否有幻觉、技术细节是否足够具体。

换句话说，这不是一个“文献综述 agent”，也不是“自动跑实验的 agent”，而是一个单篇论文阅读与报告生成 agent。

## 这个 pipeline 的核心特点

- 以“忠于原文、避免编造”为第一原则。
- 明确区分“作者原文表述”“实验支持”“谨慎解读”。
- 强调机制级技术解释，而不是只复述摘要。
- 要求把关键实验结果整理成可编辑的 Markdown 表格。
- 不重绘图片，而是推荐原文中的 Figure / Table 编号。
- 在最终写作后加入一次 review-and-revise 复审阶段。

## 流水线分解

### Stage 1: Parse and Index

文件：`prompts/01_parse_and_index.md`

目标：
- 识别论文基本元数据
- 重建章节结构
- 列出可见的图表及其原始编号
- 判断哪些章节对应动机、方法、实验、相关工作、局限性

建议输出：
- `workspace/intermediate/parsed_notes.md`

这一阶段本质上是在给后续步骤建立“索引”和“证据地图”。

### Stage 2: Extract Core Claims

文件：`prompts/02_extract_core_claims.md`

目标：
- 抽取动机
- 抽取问题设定
- 抽取主要贡献

建议输出：
- `workspace/intermediate/extraction.json` 中的
  - `basic_info`
  - `motivation`
  - `problem_setting`
  - `contributions`

这一阶段强调只保留有论文依据的事实，不提前润色。

### Stage 3: Extract Main Technology

文件：`prompts/03_extract_main_technology.md`

目标：
- 解释完整系统或模型 pipeline
- 拆解核心模块
- 说明训练目标、优化过程、推理流程
- 判断真正的新意和性能提升来源
- 解释关键专有名词，并把端到端链路按步骤拆开

建议输出：
- `workspace/intermediate/method_notes.md`
- 同时回填 `workspace/intermediate/extraction.json` 中的 `main_technology`

这是整条流水线里最重要的一步，仓库中的 `AGENT.md` 和 `configs/style_guide.md` 都要求这一部分必须讲清输入、输出、模块关系、训练和推理。

### Stage 4: Extract Experiments

文件：`prompts/04_extract_experiments.md`

目标：
- 提取数据集、benchmark、指标
- 抽取主结果、消融、定性结果
- 把关键数值结果转成 Markdown 表格

建议输出：
- `workspace/intermediate/experiment_notes.md`
- 同时回填 `workspace/intermediate/extraction.json` 中的 `experiments`、`tables`、`figures`

### Stage 5: Compare and Limitations

文件：`prompts/05_compare_and_limitations.md`

目标：
- 基于论文自身的 related work 和实验对比做谨慎比较
- 提取作者明确写出的局限性
- 补充有证据支撑的审慎推断
- 整理未来工作方向

建议输出：
- 回填 `workspace/intermediate/extraction.json` 中的
  - `comparison`
  - `limitations`
  - `future_work`

### Stage 6: Write Report

文件：`prompts/06_write_report.md`

依赖：
- `templates/report_template.md`
- `templates/extraction_template.json`
- `configs/report_schema.md`
- `configs/style_guide.md`

目标：
- 按固定结构写出完整中文论文阅读报告

输出：
- `workspace/output/final_report.md`

### Stage 7: Review and Revise

文件：`prompts/07_review_and_revise.md`

目标：
- 检查幻觉、过度推断、图表编号错误、技术解释不充分等问题
- 根据检查结果修订最终报告

建议输出：
- `workspace/intermediate/review_notes.md`
- 修订后的 `workspace/output/final_report.md`

## 仓库结构

```text
.
├── AGENT.md                          # 智能体总规则：目标、语言、写作原则、技术深度要求
├── prompts/                         # 分阶段提示词
├── scripts/
│   └── run_pipeline.py              # 适配 codex exec 的最小 orchestrator
├── templates/
│   ├── report_template.md           # 最终报告模板
│   └── extraction_template.json     # 结构化抽取模板
├── configs/
│   ├── report_schema.md             # 报告结构约束
│   ├── style_guide.md               # 中文写作与技术表达规范
│   ├── quality_checklist.md         # 质检检查项
│   └── quality_rubric.md            # 打分 rubric
└── workspace/
    ├── input/                       # 输入 PDF
    ├── intermediate/                # 中间产物
    └── output/                      # 最终报告
```

## 推荐使用方式

当前仓库已经提供了一个适配 `codex exec` 的最小 orchestrator：

- `scripts/run_pipeline.py`

它会按顺序调用 7 个阶段，自动初始化 `workspace/intermediate/extraction.json`，并把每个阶段的提示词、CLI 输出和最后一条 agent 回复保存到 `workspace/logs/run-时间戳/`。

新版工作流还会：

- 在最终报告中避免机械重复的“作者明确表述 / 实验支持”前缀，默认改为自然中文叙述
- 只对“谨慎推断”和“不确定性说明”做显式标记
- 强化 `Main Technology` 章节，使其通常成为全文最详细的部分
- 在完整 run 结束后统计各阶段以及总计的 token 使用量

### 方式 A：用 orchestrator 自动执行，推荐

这是目前最适合 `codex` 这类 CLI agent 的运行方式。

#### 前置条件

- 本机已安装 `codex` CLI
- 已完成 `codex login`
- 待分析 PDF 位于仓库内，推荐放在 `workspace/input/`

#### 一次跑完整流程

```bash
python3 scripts/run_pipeline.py \
  --pdf workspace/input/Q-vla.pdf \
  --full-auto
```

#### 只跑部分阶段

例如从抽取核心观点开始，跑到写报告为止：

```bash
python3 scripts/run_pipeline.py \
  --pdf workspace/input/Q-vla.pdf \
  --from-stage claims \
  --to-stage report \
  --full-auto
```

#### 常用参数

- `--pdf`: 输入 PDF 路径
- `--from-stage` / `--to-stage`: 控制起止阶段，可选值为 `parse`、`claims`、`method`、`experiments`、`compare`、`report`、`review`
- `--model`: 传给 `codex exec` 的模型名
- `--profile`: 传给 `codex exec` 的 profile
- `--sandbox`: sandbox 模式，默认 `workspace-write`
- `--full-auto`: 让 `codex exec` 尽量自动执行
- `--ephemeral`: 不保留 Codex session 文件
- `--force-init-extraction`: 强制用模板覆盖初始化 `workspace/intermediate/extraction.json`
- `--dry-run`: 只生成本次运行的 prompt 和 manifest，不实际调用 Codex

#### 自动运行后的产物

- 中间结果仍写入 `workspace/intermediate/`
- 最终报告写入 `workspace/output/final_report.md`
- 每次运行的日志写入 `workspace/logs/run-YYYYMMDD-HHMMSS/`

日志目录中会包含：

- `manifest.json`: 本次运行参数
- `token_usage.json`: 各阶段与整条 pipeline 的 token 汇总
- `01_parse.prompt.txt` 这类阶段 prompt
- `01_parse.stdout.log` 这类 Codex CLI 输出
- `01_parse.last_message.txt` 这类阶段收尾回复

### 方式 B：分阶段手工执行

这是最稳妥的人工控制方式，适合你想逐阶段盯质量的时候。

#### 1. 准备输入

- 把待分析论文放到 `workspace/input/`
- 建议只保留当前要分析的一篇论文，避免 agent 选错文件
- 例如可替换现有的 `workspace/input/Q-vla.pdf`

#### 2. 初始化结构化抽取文件

将模板复制为运行态文件：

```bash
cp templates/extraction_template.json workspace/intermediate/extraction.json
```

#### 3. 按顺序执行 7 个阶段

可直接对智能体下达类似指令：

```text
请先阅读 AGENT.md，然后读取 prompts/01_parse_and_index.md，
以 workspace/input/<论文文件名>.pdf 为输入，
将解析结果写入 workspace/intermediate/parsed_notes.md。
```

```text
基于 workspace/intermediate/parsed_notes.md 和原论文，
读取 prompts/02_extract_core_claims.md，
把 basic_info、motivation、problem_setting、contributions
填入 workspace/intermediate/extraction.json。
```

```text
读取 prompts/03_extract_main_technology.md，
输出 workspace/intermediate/method_notes.md，
并同步更新 workspace/intermediate/extraction.json 的 main_technology 字段。
```

```text
读取 prompts/04_extract_experiments.md，
输出 workspace/intermediate/experiment_notes.md，
并同步更新 workspace/intermediate/extraction.json 的 experiments、tables、figures 字段。
```

```text
读取 prompts/05_compare_and_limitations.md，
补全 workspace/intermediate/extraction.json 中的 comparison、limitations、future_work。
```

```text
读取 prompts/06_write_report.md、templates/report_template.md、
configs/report_schema.md、configs/style_guide.md，
基于 workspace/intermediate/extraction.json 和中间笔记，
生成 workspace/output/final_report.md。
```

```text
读取 prompts/07_review_and_revise.md、configs/quality_checklist.md、
configs/quality_rubric.md，
审查 workspace/output/final_report.md，
把审查意见写入 workspace/intermediate/review_notes.md，
并直接修订 workspace/output/final_report.md。
```

### 方式 C：单条总指令执行

如果你的 agent 支持长上下文，也可以一次性下达总任务，但稳定性通常不如分阶段执行。

可用指令模板：

```text
请阅读 AGENT.md，并严格按照 prompts/01 到 prompts/07 的顺序处理
workspace/input/<论文文件名>.pdf。
使用 templates/extraction_template.json 作为结构化抽取骨架，
使用 templates/report_template.md 生成最终报告，
使用 configs/report_schema.md、configs/style_guide.md、
configs/quality_checklist.md、configs/quality_rubric.md 进行约束和复审。

请把中间结果分别写入：
- workspace/intermediate/parsed_notes.md
- workspace/intermediate/extraction.json
- workspace/intermediate/method_notes.md
- workspace/intermediate/experiment_notes.md
- workspace/intermediate/review_notes.md

请把最终结果写入：
- workspace/output/final_report.md
```

## 建议的操作习惯

- 优先使用“分阶段执行”，不要一开始就追求一条指令跑到底。
- 每完成一个阶段就检查一次是否出现编造的图表编号、虚构数值、过度推断。
- 方法部分要回到 PDF 原文反复核对，不要只看 abstract。
- 实验部分优先保留主表、关键消融和效率结果，不要机械抄全表。
- 最终报告里应尽量保留“Figure X / Table Y 为什么值得看”的说明。

## 当前仓库的现状与注意事项

- 这是一个 prompt/config/template 驱动的流程定义仓库，目前已经补了一个最小可用的 `codex exec` 编排脚本，但还不是重型工作流系统。
- 自动执行仍依赖外部智能体环境，也就是本机可用的 `codex` CLI、账号状态和模型权限。
- `workspace/` 里的中间文件和最终文件目前大多为空，说明流程骨架已搭好，但运行结果还需要 agent 实际生成。
- `workspace/intermediate/method_notes.md` 与 `workspace/intermediate/methods_notes.md` 存在命名重复，后续建议只保留一个标准文件名。

## 最终产物应该长什么样

一个合格的 `workspace/output/final_report.md` 应至少满足：

- 有完整的 10 个顶层部分：Basic Information 到 Takeaway
- 技术部分能讲清 pipeline、模块、训练、推理、真正创新点，并且通常是全文最详细的部分
- 关键专有名词在首次出现时有简洁解释
- 实验部分包含至少一个可编辑 Markdown 表格
- 明确区分事实、证据和解释
- 不应被“作者明确表述”这类重复前缀破坏可读性
- 局限性区分“作者声明”和“审慎推断”
- 不编造图表编号、不编造实验数值

## 后续建议

如果你准备把这个仓库从“流程骨架”推进到“可运行系统”，优先级最高的补强项是：

1. 给现有 orchestrator 增加更细的阶段级校验，例如检查最终报告的 10 个顶层章节是否齐全。
2. 明确 `workspace/intermediate/extraction.json` 的字段更新策略，避免不同阶段相互覆盖。
3. 统一中间文件命名，去掉重复文件名。
4. 增加自动质检脚本，至少校验必填章节、表格存在性和空文件。
5. 增加一个样例跑通结果，便于之后做回归检查。
