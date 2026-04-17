---
name: cx-rag
description: Use this skill when answering questions about Mozilla user experience data. Queries three sources — SUMO/Kitsune forum threads, Zendesk support tickets, and the Mozilla Knowledge Base — using semantic vector search, then synthesizes a grounded, human-readable answer. Best for questions about user sentiment, common support issues, bug reports, and official guidance. Works standalone.
---

# Customer Experience RAG

**Composable:** Receives a user question, retrieves semantically similar content from three Mozilla CX indexes (SUMO/Kitsune, Zendesk, Knowledge Base), and synthesizes a grounded, human-readable answer.

**When to use:** When you need answers grounded in real Mozilla user data from SUMO forums, Zendesk tickets, and the Knowledge Base. Examples:
- What are users saying about Firefox password manager?
- What are the top pain points reported this month?
- Summarize user sentiment around a specific Firefox feature.
- What support topics are most common for mobile users?

## Overview

This skill queries three Mozilla CX data sources — SUMO/Kitsune forum threads, Zendesk support tickets, and the Mozilla Knowledge Base — using semantic vector search, then synthesizes a grounded, factual response from the retrieved context. Each source is queried on every invocation; results are labeled by source so the answer can draw on user sentiment (Kitsune), bug reports (Zendesk), and official guidance (Knowledge Base).

## Data Sources

The orchestrator queries all three sources on every invocation and returns labeled sections.

| Source | Table | Search method |
|--------|-------|--------------|
| Kitsune / SUMO / Mozilla Support | `kitsune_retrieval_index` | `VECTOR_SEARCH` — semantic similarity via embedding |
| Zendesk | `zendesk_retrieval_index` | `VECTOR_SEARCH` — semantic similarity via embedding |
| Knowledge Base | `knowledge_base_retrieval_index` | `VECTOR_SEARCH` — semantic similarity via embedding |

### Kitsune (= SUMO = Mozilla Support)

Kitsune is the application powering support.mozilla.org. The three names refer to the same source. It contains forum threads posted by Firefox users, along with answers from other users, Mozilla Staff, and the knowledge base. This is the **primary source for sentiment analysis and user feedback**: use `sentiment_score`, `content`, and `answer_content` to understand how users feel and what they are experiencing.

**Columns:** `title`, `content`, `answer_content`, `summary_generated`, `category_generated`, `sentiment_score`, `recency_score`, `product`, `topic`

### Zendesk

Zendesk is a ticket management application used to track Firefox issues and bugs reported by users. It contains structured support tickets. Although a `sentiment_score` column is present, **it does not reliably reflect user sentiment** — do not use it for sentiment analysis. Instead, use Zendesk to understand **what problems users are reporting**, the nature of bugs, and the reasons behind negative experiences.

**Columns:** `title`, `content`, `summary_generated`, `category_generated`, `sentiment_score`, `product`, `star_rating`, `recency_score`

### Knowledge Base

The Knowledge Base is a curated set of articles written to answer user questions and solve common problems — the same content that Mozilla Support staff reference when replying to forum posts or Zendesk tickets. Use this source to understand what official guidance exists for a given topic, not to measure how users feel. Do not use `sentiment_score` from this source — it is not meaningful for KB articles.

**Columns:** `title`, `summary_generated`, `category_generated`, `slug`

The `slug` field maps to a live article URL: `support.mozilla.org/kb/<slug>`. Include this link when referencing a KB article in your answer.

See `references/kitsune_schema.md`, `references/zendesk_schema.md`, and `references/knowledge_base_schema.md` for full column details per source.

## 🚨 REQUIRED — Follow These Steps on Every Invocation

**Never fabricate or infer data. All answers must be grounded in what the retrieved documents actually contain.**

### Step 1: Clarify the date range — STOP and ask or confirm before running

Date context is required for grounded answers. **Do not run the script until the date range is confirmed.**

#### 1a. If a date range CAN be inferred from the question

Map it to `--date-from` / `--date-to` using these rules:
- "March 2026" → `2026-03-01` / `2026-03-31`
- "Q1 2026" → `2026-01-01` / `2026-03-31`
- "last month" → compute from today's date
- "this year" → `YYYY-01-01` / today

Then confirm with the user before running:

> I'll query **[Month Year]** (`YYYY-MM-DD` to `YYYY-MM-DD`). Is that the right period?

Wait for the user to confirm or correct. Only proceed once confirmed.

#### 1b. If NO date range can be inferred

Ask the user directly — do not guess or use a default:

> To ground the answer in real data, I need a time period. Which period should I query? (e.g. "March 2026", "Q1 2026", "last 30 days")

Wait for the response, then proceed as in 1a.

#### Other filters (product, locale)

Parse these from the question and apply silently — no confirmation needed:

| What the user says | Flag | Example value |
|--------------------|------|---------------|
| Product ("Firefox for Android", "Fenix", "desktop") | `--product` | `Firefox for Android` |
| Language / country ("Spanish users", "in France", "en-US") | `--locale` | `es` / `fr` / `en-US` |

**Filter coverage by source:**

| Filter | Kitsune | Zendesk | Knowledge Base |
|--------|---------|---------|----------------|
| `--date-from` / `--date-to` | yes | yes | no (no date column) |
| `--product` | yes | yes | yes |
| `--locale` | yes | yes | yes |

When a filter doesn't apply to a source (e.g. date on KB), that source is still queried without the filter — mention this in the answer.

### Step 2: Retrieve context

Run the orchestrator script with the user's question and any inferred filters:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/cx-rag/scripts/orchestrator.py \
  --question "<user question here>" \
  [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD] \
  [--product "<product name>"] [--locale "<locale code>"]
```

The script embeds the question using `gemini-embedding-001`, runs `VECTOR_SEARCH` against all three indexes, and returns the top-5 most semantically similar documents per source.

### Step 3: Synthesize the answer

If all three sources return no results, stop and tell the user — do not fabricate content. Suggest one of: (1) broadening the date range, (2) relaxing or removing product/locale filters, (3) rephrasing the question with different keywords.

Read the returned context blocks and compose a response that:
- Opens by naming which sources contributed and how many results, e.g. "Based on 5 SUMO/Kitsune threads, 3 Zendesk tickets, and 2 Knowledge Base articles..."
- Directly answers the user's question using only retrieved content
- Is written in plain, human language — no SQL, no column names, no jargon
- **Sentiment:** only draw sentiment conclusions from **Kitsune** results — `sentiment_score` in Zendesk and Knowledge Base does not reflect user sentiment and must not be used for that purpose
- Use **Zendesk** results to describe what problems or bugs users are reporting, not how they feel
- Use **Knowledge Base** results to describe what official guidance or solutions exist for a topic
- Calls out specific categories or topics when they add insight
- Uses `distance` (cosine distance, 0–2 scale) to signal retrieval confidence: below ~0.3 is a strong match, above ~0.6 means the results are only loosely related to the question — note this when it affects the answer's reliability

Use the template in `assets/answer_template.md` as a guide.

### Step 4: Invite follow-up

End every response with:
> *Is this answer helpful, or would you like me to refine the search or dig deeper into a specific aspect?*

## Quick Start

User asks: *"What are users complaining about with Firefox sync?"*

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/cx-rag/scripts/orchestrator.py --question "What are users complaining about with Firefox sync?"
```

Claude reads the returned context blocks and responds:

> Based on 5 SUMO/Kitsune support threads, users are primarily frustrated with Firefox Sync failing to sync bookmarks across devices (average sentiment ~-0.6). Common themes include login loops, missing bookmarks after major updates, and confusion around account management. Top categories: Sync & Accounts, Bookmarks.
>
> *Is this answer helpful, or would you like me to dig deeper into a specific aspect?*

## Common Workflows

### Workflow 1: Sentiment question

User: *"What do users feel about the new Firefox home screen?"*

1. Run `python ${CLAUDE_PLUGIN_ROOT}/skills/cx-rag/scripts/orchestrator.py --question "What do users feel about the new Firefox home screen?"`
2. Read the sentiment scores and summaries in the returned documents
3. Aggregate sentiment direction (positive/negative/mixed) and name top themes
4. Report with plain-language sentiment framing

### Workflow 2: Topic discovery

User: *"What are the most common issues for Firefox on Android?"*

1. Run the script with the question
2. Group the returned documents by `categories` and `topics` fields
3. Summarize the 3-5 most frequent themes with brief explanations

### Workflow 3: Language/locale-scoped search

User: *"What are Spanish-speaking users saying about Firefox sync?"*

1. Parse `--locale es` from "Spanish-speaking"
2. Run the script with `--locale es` — filters Kitsune, Zendesk, and KB to Spanish content
3. Note in the answer that date and product filters still apply to Kitsune and Zendesk; KB is filtered only by locale

### Workflow 4: Deeper search

If the initial top-5 results feel thin or off-topic:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/cx-rag/scripts/orchestrator.py --question "<refined question>" --top-k 10
```

Refine the question to be more specific, or increase `--top-k` for broader coverage.

## Script Reference

### `scripts/orchestrator.py`

Embeds the user's question via Vertex AI and runs `VECTOR_SEARCH` against all three indexes (Kitsune, Zendesk, Knowledge Base) in parallel. Returns the top-K matching documents per source as formatted context blocks to stdout.

```
Usage: python ${CLAUDE_PLUGIN_ROOT}/skills/cx-rag/scripts/orchestrator.py
         --question "<your question>"
         [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD]
         [--product "<name>"] [--locale "<code>"]
         [--top-k N] [--inspect]

Options:
  --question TEXT        The question to search for (required)
  --date-from YYYY-MM-DD Filter records on or after this date (Kitsune + Zendesk)
  --date-to   YYYY-MM-DD Filter records on or before this date (Kitsune + Zendesk)
  --product   TEXT       Partial-match filter on product name (Kitsune + Zendesk)
  --locale    TEXT       Partial-match filter on locale/language code (all sources)
  --top-k     INT        Number of documents to retrieve per source (default: 5)
  --inspect              Print all table schemas and exit
```

**Prerequisites:** Google Cloud SDK (`gcloud` + `bq` CLI) and active credentials. No pip installs required.

To authenticate, run both commands using the project name provided by DE:
```bash
gcloud auth application-default login
gcloud config set project <project-name-from-DE>
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Authentication rejected (401)` | Expired or missing credentials | Re-run `gcloud auth application-default login` |
| `No GCP project configured` | Project not set | Run `gcloud config set project <project-name-from-DE>` |
| `API error: ...` on `--inspect` | Table doesn't exist or permission denied | Confirm the project name with DE and re-authenticate |
| All sources return 0 results | Filters too narrow or question out of scope | Broaden date range, remove product/locale filters, or rephrase |
| Fewer results than `--top-k` | Post-filter reduced the set (expected when filters are active) | Increase `--top-k` to fetch more candidates before filtering |

## Key Files

| File | Purpose |
|------|---------|
| `scripts/orchestrator.py` | Embeds question + runs vector search — call on every invocation |
| `assets/example_questions.md` | Sample questions this skill handles well — use to set user expectations |
| `assets/answer_template.md` | Template for structuring synthesized answers |
| `references/kitsune_schema.md` | Schema reference for `kitsune_retrieval_index` (SUMO/Kitsune) |
| `references/sumo_kitsune_overview.md` | What SUMO and Kitsune are; data freshness and known limitations |
| `references/zendesk_schema.md` | Schema reference for `zendesk_retrieval_index` |
| `references/zendesk_overview.md` | What Zendesk is; how to interpret ticket data and limitations |
| `references/knowledge_base_schema.md` | Schema reference for `knowledge_base_retrieval_index` |
| `references/knowledge_base_overview.md` | What the Mozilla Knowledge Base is; filter constraints and limitations |
