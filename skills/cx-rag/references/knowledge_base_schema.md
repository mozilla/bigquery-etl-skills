# knowledge_base_retrieval_index Schema Reference

**Table:** `<project>.customer_experience_derived.knowledge_base_retrieval_index`
**Purpose:** Semantic search index over Mozilla Knowledge Base articles, pre-embedded for vector similarity queries.

## Columns used by the orchestrator

| Column | BigQuery Type | Description |
|--------|--------------|-------------|
| `title` | STRING | Article title |
| `summary_generated` | STRING | LLM-generated summary of the article |
| `category_generated` | STRING | LLM-generated high-level category |
| `slug` | STRING | URL slug — maps to `support.mozilla.org/kb/<slug>` |

## Columns available for filtering (not fetched)

| Column | BigQuery Type | Description |
|--------|--------------|-------------|
| `locale` | STRING | Article language/locale — used by `--locale` filter |
| `embedding` | FLOAT REPEATED | Vector for similarity search (`gemini-embedding-001`) |

## Filter coverage

The Knowledge Base table has **no `creation_date` or `product` columns** — `--date-from`, `--date-to`, and `--product` filters do not apply. Only `--locale` is supported.

## Full schema

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `id` | INTEGER | NULLABLE | Article ID |
| `title` | STRING | NULLABLE | Article title |
| `html` | STRING | NULLABLE | Full article HTML content |
| `slug` | STRING | NULLABLE | URL slug — maps to `support.mozilla.org/kb/<slug>` |
| `is_template` | BOOLEAN | NULLABLE | Whether the article is a template |
| `is_localizable` | BOOLEAN | NULLABLE | Whether the article can be localized |
| `locale` | STRING | NULLABLE | Article language/locale |
| `category` | INTEGER | NULLABLE | Category ID |
| `allow_discussion` | BOOLEAN | NULLABLE | Whether discussions are enabled |
| `needs_change` | BOOLEAN | NULLABLE | Whether the article is flagged for review |
| `share_link` | STRING | NULLABLE | Shareable link for the article |
| `display_order` | INTEGER | NULLABLE | Display order within the category |
| `current_revision_id` | INTEGER | NULLABLE | ID of the current published revision |
| `num_pageviews_last_7_days` | INTEGER | NULLABLE | Pageview count over last 7 days |
| `num_pageviews_last_30_days` | INTEGER | NULLABLE | Pageview count over last 30 days |
| `num_pageviews_last_90_days` | INTEGER | NULLABLE | Pageview count over last 90 days |
| `num_pageviews_last_365_days` | INTEGER | NULLABLE | Pageview count over last 365 days |
| `summary_generated` | STRING | NULLABLE | LLM-generated summary |
| `category_generated` | STRING | NULLABLE | LLM-generated category |
| `language_generated` | STRING | NULLABLE | LLM-detected language |
| `entities_generated` | STRING | REPEATED | LLM-extracted entities |
| `topics_generated` | STRING | REPEATED | LLM-generated topic tags |
| `sentiment_score` | FLOAT | NULLABLE | Sentiment score — **do not fetch or use; not meaningful for KB articles** |
| `metadata` | RECORD | NULLABLE | Additional metadata fields |
| `embedding` | FLOAT | REPEATED | Vector for similarity search (`gemini-embedding-001`) |

## Embedding model

All embeddings use `gemini-embedding-001` via Vertex AI. The orchestrator embeds the user's question with the same model at query time — dimensionality must match.

## How VECTOR_SEARCH is used

```sql
SELECT base.title, base.summary_generated, base.category_generated,
       base.slug,
       distance, 'knowledge_base' AS _source
FROM VECTOR_SEARCH(
    TABLE `<project>.customer_experience_derived.knowledge_base_retrieval_index`,
    'embedding',
    (SELECT <query_embedding> AS embedding),
    top_k => 5,
    distance_type => 'COSINE'
)
[WHERE base.locale LIKE '%en-US%']
ORDER BY distance ASC
```

Lower `distance` = more semantically similar to the question.

## Using the slug field

The `slug` column maps directly to a live article URL:

```
https://support.mozilla.org/kb/<slug>
```

Always include this link when referencing a Knowledge Base article in an answer.
