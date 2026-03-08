Write the final Markdown reading report from the paper, the evidence pack, and the structured extraction.

Source priority:
1. the paper PDF
2. `workspace/intermediate/evidence_pack.md`
3. `workspace/intermediate/extraction.json`

Use the evidence pack as your main working memory, but verify important claims against the PDF when needed.
Treat `workspace/intermediate/extraction.json` as a structured index, not as a prose source that should control the final writing style.

Requirements:
- Follow `templates/report_template.md`, `configs/report_schema.md`, and `configs/style_guide.md`.
- Write natural, rigorous Chinese prose.
- Keep the Main Technology section as the deepest section unless the paper is primarily empirical.
- Reconstruct the end-to-end pipeline clearly enough that a technical reader could redraw it.
- Let experiments support the method analysis rather than dominate it.
- Use editable Markdown tables for key quantitative results.
- Integrate source attribution naturally inside sentences.
- Only keep explicit markers such as `谨慎推断` or `不确定性说明` when they add real signal.

Avoid:
- mechanically copying bullet labels from intermediate artifacts
- turning the report into a JSON-to-Markdown rewrite
- broad claims not supported by the paper
