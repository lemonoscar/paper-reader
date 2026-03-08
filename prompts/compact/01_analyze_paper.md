Perform one comprehensive analysis pass over the paper and build durable downstream context.

This stage replaces fragmented `parse / claims / method / experiments / compare` notes.

Your job:
1. Read the paper PDF as the primary source.
2. Use `templates/evidence_pack_template.md` as the structural target for `workspace/intermediate/evidence_pack.md`.
3. Fully populate `workspace/intermediate/extraction.json`.
4. Keep both outputs tightly grounded in the paper.

Important priorities:
- This is the main comprehension stage. Do not split understanding across extra scratch files.
- `workspace/intermediate/evidence_pack.md` should preserve the reasoning-critical evidence that a later writing stage would otherwise lose.
- Prefer direct evidence anchors such as section names, figure numbers, table numbers, and explicit uncertainty notes.
- When the PDF includes supplementary material, use it, but clearly distinguish main-paper evidence from supplement-only evidence when that distinction matters.

What the evidence pack must capture:
- title, authors, venue/year if available
- section map and where key evidence lives
- motivation, problem setting, and contributions
- complete method reconstruction: inputs, outputs, end-to-end pipeline, module roles, training, inference, deployment
- experimental evidence: datasets, metrics, main tables, ablations, qualitative findings, efficiency/deployment evidence
- comparison boundaries, limitations, future work
- unresolved ambiguities, inconsistencies, and missing details
- recommended original figures/tables to inspect

Requirements:
- Be concrete and mechanism-level, especially for the method.
- Use Chinese by default.
- Do not write polished final-report prose yet.
- Do not invent figure/table numbers, values, metadata, or losses.
- If extraction JSON and evidence notes differ in granularity, keep them consistent on facts and put the richer explanation in `evidence_pack.md`.
- Remove placeholder items from `workspace/intermediate/extraction.json` when they are not supported by the paper.
