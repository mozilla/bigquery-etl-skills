# Answer Template

Use this structure when synthesizing a response from the retrieved context blocks.
Adapt the sections — not every question needs all of them.

---

**Based on [N] SUMO/Kitsune threads, [N] Zendesk tickets, and [N] Knowledge Base articles:**

[1–2 sentence direct answer to the question, grounded in the documents.]

**Key themes:**
- **[Theme 1]** — [Brief explanation. Include sentiment direction if from Kitsune, e.g. "users are frustrated, avg sentiment ~-0.5"]
- **[Theme 2]** — [Brief explanation]
- **[Theme 3]** — [Brief explanation]

**Sentiment signal:** [Only draw from Kitsune results. E.g.: "Sentiment ranges from -0.7 to 0.1 (average ~-0.4), indicating users feel negatively about this topic." Do NOT report sentiment from Zendesk or Knowledge Base as user sentiment.]

**What users are reporting (Zendesk):** [Only include when Zendesk results add distinct signal. Describe the bugs or problems users are filing tickets about, not how they feel.]

**Official guidance (Knowledge Base):** [Only include when KB results are relevant. Summarize what Mozilla's official articles say about the topic. KB slugs map to support.mozilla.org/kb/<slug>.]

**Top categories:** [List the categories that appeared most in the retrieved documents]

---

*Is this answer helpful, or would you like me to refine the search or dig deeper into a specific aspect?*

---

## Notes on grounding

- Only reference what appears in the retrieved documents. Do not add background knowledge.
- If the documents don't answer the question well, say so and suggest refining the query or broadening the date range.
- Avoid quoting raw `content` fields verbatim unless the user asks for specific quotes.
- Sentiment scores are per-document — average or describe the range, don't cherry-pick.
- If a source returns no results, omit its section rather than saying "no results found."
- If all sources return no results, tell the user and suggest: (1) broadening the date range, (2) relaxing product/locale filters, or (3) rephrasing the question with different keywords.
