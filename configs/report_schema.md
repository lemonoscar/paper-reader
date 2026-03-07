# Report Schema

## 1. Purpose

This document defines the required structure and content schema for the final Markdown paper reading report.

The report must be:
- structured
- evidence-based
- technically precise
- faithful to the source PDF
- explicit about uncertainty

The report is not a free-form summary. It must follow the schema below.

---

## 2. Required Top-level Sections

A valid report must contain the following sections in order. Chinese headings are preferred; English equivalents are acceptable:

1. Basic Information / 基本信息
2. Motivation / 研究动机
3. Problem Setting / 问题设定
4. Main Contributions / 主要贡献
5. Main Technology / 主要技术
6. Experiments and Key Results / 实验与关键结果
7. Comparison with Other Works / 与已有工作的比较
8. Drawbacks and Limitations / 局限性
9. Future Work / 未来工作
10. Takeaway / 总结

---

## 3. Section-by-Section Requirements

### 3.1 Basic Information

Must include:
- paper title
- authors if available
- venue and year if available
- research area / topic
- a short list of keywords

Must not include:
- fabricated venue/year
- unsupported metadata guesses

---

### 3.2 Motivation

Must answer:
- what problem the paper aims to solve
- why the problem matters
- what gap or limitation in prior work motivates this paper

Preferred evidence sources:
- abstract
- introduction
- related work
- problem statement

Should avoid:
- generic statements without paper-specific grounding

---

### 3.3 Problem Setting

Must include:
- task definition
- input/output formulation
- assumptions or constraints
- evaluation setting if clearly stated

Should clarify:
- whether the task is offline/online, supervised/self-supervised/RL, simulated/real-world, etc., when applicable

Must not:
- infer a formal task setup if the paper does not define one clearly

---

### 3.4 Main Contributions

Must include:
- 2 to 5 concise bullet points
- each contribution should be specific and paper-grounded

Good contributions are:
- introducing a new method/component/objective/benchmark/system
- providing a new experimental finding
- improving a measurable capability under a clear setting

Bad contributions are:
- vague praise
- restating the entire paper in one sentence
- unsupported novelty claims

---

### 3.5 Main Technology

This is the most important section.
It should usually be the longest and most detailed section in the report, especially for robotics, VLA, LLM, or system papers.

Must include the following subparts:
- overall idea
- full pipeline / architecture / system flow
- step-by-step end-to-end pipeline from raw input or data collection to final output / deployment
- core modules and their functions
- key terminology or notation explained on first mention
- training objective / optimization / learning procedure
- inference / test-time / deployment procedure
- what is genuinely novel
- what is likely the main source of improvement

For each major module, try to explain:
- input
- output
- transformation or function
- role in the whole system

Should reference useful original figures where possible.
Should make it possible for a technically trained reader to redraw the pipeline from the description.

Must not:
- stay only at high-level intuition
- merely paraphrase the abstract
- use vague phrases like "novel framework" without details
- let result narration crowd out the method explanation

---

### 3.6 Experiments and Key Results

Must include:
- datasets / benchmarks
- evaluation metrics
- main quantitative findings
- ablation or analysis findings if present
- qualitative findings if present

Must include at least one editable Markdown table when quantitative results exist.

The table should prioritize:
1. main result table
2. key ablation table
3. efficiency/runtime/resource table if important

Should also include:
- recommended original tables/figures for reference
- a short explanation of why each table/figure matters
- concise interpretation of what the most important results imply for the method

Must not:
- fabricate missing values
- dump all tables from the paper without prioritization
- become longer and more detailed than the Main Technology section unless the paper is primarily empirical

---

### 3.7 Comparison with Other Works

Must compare primarily based on:
- the paper's related work section
- explicitly named baselines
- experimental comparison targets

Should include:
- task setting differences
- methodological differences
- likely strengths and weaknesses
- what distinguishes this paper

Must remain cautious:
- do not pretend to provide a full literature survey
- do not over-interpret limited evidence

A comparison table is preferred.

---

### 3.8 Drawbacks and Limitations

Must separate:
- author-stated limitations
- cautious additional observations

Possible categories:
- generalization
- robustness
- efficiency
- scalability
- data requirements
- deployment constraints
- evaluation limitations

Must not:
- present speculative criticism as fact

---

### 3.9 Future Work

Should include:
- future directions explicitly mentioned by the authors
- reasonable extension directions derived from the limitations

Must remain grounded in the paper.

---

### 3.10 Takeaway

Must include:
- a concise synthesis of why the paper matters
- what is most worth learning from it
- what kind of reader or research direction it is most relevant to

Should be short and high-density.

---

## 4. Global Constraints

The report must:
- be written in Markdown
- preserve scientific rigor
- distinguish fact from interpretation
- explicitly mark uncertainty when needed
- avoid fabrication
- avoid hype language
- read naturally in Chinese instead of looking like a mechanically labeled evidence dump
- explain important specialized terms on first mention

The report must not:
- invent figure/table numbers
- invent equations or losses not supported by the paper
- exaggerate novelty
- make broad claims without evidence
- mechanically prefix every bullet with labels such as "作者明确表述", "论文原文表述", or "实验支持"

---

## 5. Output Conventions

When appropriate, the report should distinguish evidence sources through natural phrasing, such as:

- "论文指出……"
- "主文 Table 2 显示……"
- "补充材料中的实验表明……"

Use explicit markers mainly for:

- `谨慎推断`
- `不确定性说明`

For figures/tables:
- do not embed images
- instead recommend original figure/table numbers and describe their role

For quotes:
- use only short, necessary quotes
- prefer paraphrase for most content
