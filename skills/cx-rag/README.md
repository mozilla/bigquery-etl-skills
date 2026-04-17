# cx-rag — Customer Experience RAG Skill

A Retrieval-Augmented Generation (RAG) skill that answers questions about Mozilla user experience. It retrieves semantically similar content from three live data sources — SUMO/Kitsune support forums, Zendesk tickets, and the Mozilla Knowledge Base — then synthesizes a grounded, factual answer based solely on what those sources contain.

## Prerequisites

Before using this skill you need:

1. **Google Cloud SDK** installed — [install gcloud](https://cloud.google.com/sdk/docs/install)
2. **Authenticated** with application-default credentials:
   ```bash
   gcloud auth application-default login
   ```
3. **GCP project set** to the project name provided by your DE team:
   ```bash
   gcloud config set project <project-name-from-DE>
   ```

## Installation

Install the bigquery-etl-skills plugin in Claude Code (one-time setup):

```bash
/plugin marketplace add https://github.com/mozilla/bigquery-etl-skills.git
/plugin install bigquery-etl-skills
```

## How to Use

Just ask Claude a question about user experience. The skill is invoked automatically — no special command needed.

> What are users saying about Firefox sync this quarter?

> What are the top pain points for Firefox on Android in March 2026?

> Summarize user sentiment around the new Firefox home screen.

Claude will confirm the date range before querying, retrieve relevant documents from all three sources, and synthesize a human-readable answer grounded in actual user data.

## Filters

You can scope your question by time period, product, or language — just include them naturally in your question or specify them directly.

| Filter | How to specify | Example |
|--------|----------------|---------|
| Date range | Say the period in your question | "in Q1 2026", "last month", "March 2026" |
| Product | Name the product | "Firefox for Android", "Fenix", "Firefox desktop" |
| Language / locale | Name the language or locale code | "Spanish users", "in French", "en-US" |

**Coverage by source:**

| Filter | Kitsune | Zendesk | Knowledge Base |
|--------|---------|---------|----------------|
| Date range | yes | yes | no (no date column) |
| Product | yes | yes | yes |
| Locale | yes | yes | yes |

## Example Questions

**Sentiment:**
- What do users feel about Firefox password manager?
- Which Firefox features are users most frustrated with?

**Topic discovery:**
- What are the most common support topics for Firefox on Android?
- What issues do users report after major Firefox updates?

**Pain points:**
- What login or account issues come up most frequently?
- What are users complaining about with Firefox sync?

**Summaries:**
- Give me a summary of user feedback about Firefox for iOS.
- What are the main themes in SUMO for the Search & Navigation category?

## Tips

- Be specific about the feature area ("Firefox sync bookmarks" vs. "Firefox sync")
- Always include a time period — the skill will ask if you don't
- If results feel thin, ask Claude to broaden the date range or increase the result count

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Authentication rejected (401)` | Re-run `gcloud auth application-default login` |
| `No GCP project configured` | Run `gcloud config set project <project-name-from-DE>` |
| Answer says "no results found" | Broaden the date range, remove product/locale filters, or rephrase your question |
| Fewer results than expected | Ask Claude to search with a higher result count (`--top-k 10`) |
