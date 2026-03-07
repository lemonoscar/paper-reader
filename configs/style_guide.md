# Style Guide

## 1. Overall Writing Style

The report should be written in fluent, natural, scientifically rigorous Chinese.

Target style:
- clear
- precise
- structured
- high-information-density
- academically neutral

The tone should be:
- formal but readable
- analytical rather than promotional
- explanatory rather than decorative

Avoid:
- exaggerated praise
- vague buzzwords
- unnecessary repetition
- overlong rhetorical paragraphs

---

## 2. Core Principles

### 2.1 Precision over flourish

Prefer precise technical wording over elegant but empty phrasing.

Good:
- "该方法将视觉编码器输出的特征与动作条件拼接后送入策略头。"

Bad:
- "该方法巧妙地融合了多模态信息，从而实现了更强大的决策能力。"

---

### 2.2 Mechanism-level explanation

When describing technology, explain how the method works, not just what it aims to do.

Good:
- "模型首先从观测中提取时序特征，再通过跨模态注意力将语言条件注入策略表示。"

Bad:
- "模型通过有效的信息融合实现了性能提升。"

---

### 2.3 Evidence-based claims

Whenever possible, tie claims to evidence.

Preferred phrasing:
- "论文指出……"
- "从 Table 2 可以看出……"
- "实验结果表明……"
- "根据作者在 Section 4.3 的分析……"

Avoid unsupported phrasing:
- "显然……"
- "毫无疑问……"
- "这说明该方法具有普适性……" unless evidence is strong

---

### 2.4 Distinguish summary from interpretation

Use clear boundaries between:
- what the paper explicitly says
- what the experiments support
- what is your cautious interpretation

Prefer natural phrasing inside the sentence rather than repetitive labels at the start of every bullet.

Good:
- "论文将任务写为 μ: S × W → A。"
- "主文 Table 2 显示，QUART 在 8 个列项上全部最好。"
- "谨慎推断：这一收益可能同时来自动作表示和数据规模。"

Avoid:
- every bullet starts with "作者明确表述："
- every bullet starts with "实验支持："
- turning the final report into a mechanically labeled evidence dump

---

### 2.5 Technical density is preferred

The report should be concise but information-dense.

Each paragraph should ideally contain:
- one main idea
- one supporting detail
- one concrete implication when useful

Avoid paragraphs that only contain:
- praise
- repetition
- abstract summary without mechanism

---

### 2.6 Explain terms on first mention

Important specialized terms, abbreviations, and paper-specific objects should be explained briefly on first appearance.

Good:
- "`behavior cloning`（行为克隆）指直接从示范轨迹监督学习动作映射。"
- "`Detokenize` 在本文中是把离散动作 token 还原为连续高层控制命令的步骤。"

Bad:
- first use a term like `symbol tuning`, `causal masking`, or `command-tracking controller` without any explanation
- assume the reader already knows paper-specific abbreviations

---

## 3. Section-Specific Guidance

### 3.1 Motivation

Should:
- explain the specific problem context
- identify the limitation of prior work
- make the motivation paper-specific

Should not:
- become a generic introduction to the whole field

---

### 3.2 Main Contributions

Should:
- be short, concrete, and enumerated
- focus on what this paper actually adds

Avoid:
- contribution bullets that are just rewritten motivation
- bullets that merge multiple ideas into one vague claim

---

### 3.3 Main Technology

This section must be the deepest and most concrete.
It should usually be the longest section in the report.

Preferred organization:
1. overall idea
2. full pipeline
3. key modules
4. training
5. inference
6. terminology
7. novelty

When possible, explain:
- information flow
- module interfaces
- supervision signals
- optimization targets
- deployment implications
- why each pipeline step exists
- how outputs from one step become inputs to the next

Avoid:
- only intuitive descriptions
- restating introduction text
- skipping training/inference details
- listing modules without connecting them into a full pipeline
- spending more space on result recap than on the actual method

For robotics / VLA / LLM / system papers, explicitly trace:
- observation or data collection
- representation / tokenizer / encoder
- backbone or core model
- output or action representation
- controller / tool / executor / deployment loop
- any closed-loop or sim-to-real link if the paper includes one

---

### 3.4 Experiments

Should:
- focus on evidence, not narration
- summarize benchmark, metrics, and key findings efficiently
- use tables when numbers matter
- support the explanation of the method rather than replace it

Preferred phrasing:
- "在 X benchmark 上，作者报告了……"
- "相较于 baseline A，该方法在 Y 指标上提升了……"
- "消融实验表明……"

Avoid:
- copying table values without interpretation
- listing too many secondary results without prioritization
- letting the experiments section overshadow the Main Technology section for a method-heavy paper

---

### 3.5 Comparison with Other Works

Should:
- compare task setting, assumptions, and core technique
- identify the real difference rather than superficial wording differences

Avoid:
- pretending to know the whole literature
- broad ranking claims without support

---

### 3.6 Limitations

Should:
- be sober and specific
- separate author-stated vs inferred limitations

Avoid:
- aggressive criticism
- speculative weakness claims without evidence

---

## 4. Forbidden Style Patterns

Do not use language that is:
- promotional
- emotional
- overly absolute
- content-empty

Examples to avoid:
- "非常惊艳"
- "革命性突破"
- "极大地推动了该领域发展"
- "效果非常优秀"
- "设计十分巧妙"

Unless backed by explicit and strong evidence, avoid absolute words such as:
- "完全"
- "彻底"
- "显著优于所有方法"
- "普遍适用"

---

## 5. Preferred Structural Patterns

Prefer:
- short subsections
- bullet lists for contributions and limitations
- markdown tables for quantitative comparisons
- one idea per paragraph
- explicit transitions between sections

Useful transition examples:
- "从问题设定上看，……"
- "在方法层面，核心改动主要体现在……"
- "实验部分最关键的证据来自……"
- "与已有工作相比，真正的差异在于……"
- "需要注意的是，该论文的结论仍受到……限制"

---

## 6. Quote Policy

Use direct quotes only when:
- the paper defines a key concept
- the wording of a contribution claim matters
- the exact phrasing is scientifically important

Otherwise, paraphrase.

Quotes should be:
- short
- accurate
- clearly attributed

---

## 7. Good vs Bad Examples

### Example 1

Bad:
"本文提出了一个新颖而高效的框架，并且取得了非常显著的提升。"

Good:
"本文提出的核心改动是在策略学习前加入显式的状态抽象模块。根据作者报告的主结果表，该设计在两个 manipulation benchmark 上相较基线取得了更高成功率。"

---

### Example 2

Bad:
"该模型通过多模态融合更好地理解任务。"

Good:
"该模型先编码视觉观测与语言指令，再利用跨模态注意力将语言条件注入动作生成过程，因此语言信息并非只在输入端拼接，而是持续参与策略表示构建。"

---

### Example 3

Bad:
"该工作未来潜力巨大。"

Good:
"该方法未来可以沿两个方向扩展：一是验证其在更长时序任务中的稳定性，二是测试其在真实机器人部署时对感知噪声的鲁棒性。"
