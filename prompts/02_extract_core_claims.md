Based on the parsed notes and the paper PDF, extract the core factual content for the following sections:

- Motivation
- Problem setting
- Main contributions

Requirements:
1. Extract only claims that are supported by the paper.
2. Preserve the distinction between:
   - author-explicit statements
   - evidence-supported observations
   - cautious interpretation
   but keep the extraction JSON readable and clean.
3. Do not prepend every JSON entry with labels such as "作者明确表述：" or "证据支持观察：".
4. Use explicit markers only when the content is genuinely inferential or uncertain, for example "谨慎推断：" or "论文未明确说明：".
5. Use concise structured bullets or short factual statements.
6. Avoid polished prose for now.
7. Save into the extraction JSON.
