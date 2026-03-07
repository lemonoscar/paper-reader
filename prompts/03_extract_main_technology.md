Explain and extract the paper's core technology in a mechanism-level manner.

You must answer:
1. What are the inputs and outputs?
2. What is the full system or model pipeline?
3. What are the core modules?
4. What does each core module do?
5. How is the model trained?
6. What is the training objective or loss?
7. How does inference work?
8. What is genuinely novel compared with prior work?
9. What is likely the main source of performance improvement?

Requirements:
- avoid vague wording
- do not simply restate the abstract
- make this the deepest stage; for most papers it should be more detailed than the experiments stage
- reconstruct the pipeline as an ordered chain, not just as a bag of modules
- prefer concrete descriptions of data flow, architecture, training, inference, and deployment
- for robotics / VLA / LLM / system papers, explicitly trace:
  - data collection or raw observation
  - tokenizer / encoder / representation step
  - backbone or main model
  - output or action representation
  - controller / tool / executor / deployment loop
- for each major module, explain input, output, transformation, why it is needed, and how it connects to adjacent modules
- explain specialized terms and abbreviations on first mention; add a short terminology subsection in `method_notes.md` when useful
- if some details are missing, explicitly say so
- list recommended figures for understanding the method
- when updating `workspace/intermediate/extraction.json`, fill `main_technology.overall_pipeline`, `pipeline_steps`, `core_modules`, `key_terms`, `training_objective`, `inference_process`, `novelty`, and `performance_gain_hypothesis` whenever the paper provides enough evidence
