# zendesk_retrieval_index Schema Reference

**Table:** `<project>.customer_experience_derived.zendesk_retrieval_index`
**Purpose:** Semantic search index over Zendesk support tickets, pre-embedded for vector similarity queries.

## Columns used by the orchestrator

| Column | BigQuery Type | Description |
|--------|--------------|-------------|
| `title` | STRING | Ticket subject or title |
| `content` | STRING | Full ticket body text |
| `summary_generated` | STRING | LLM-generated summary of the ticket |
| `category_generated` | STRING | LLM-generated high-level category |
| `sentiment_score` | FLOAT | Sentiment score -1.0 to 1.0 — **not reliable as a user sentiment signal; use Kitsune for sentiment analysis** |
| `product` | STRING | Firefox product the ticket relates to |
| `star_rating` | STRING | User-provided star rating for the support interaction |
| `recency_score` | FLOAT | Recency weight for ranking |

## Columns available for filtering (not fetched)

| Column | BigQuery Type | Description |
|--------|--------------|-------------|
| `creation_date` | TIMESTAMP | When the ticket was created — used by `--date-from` / `--date-to` filters |
| `locale` | STRING | Ticket language/locale — used by `--locale` filter |
| `embedding` | FLOAT REPEATED | Vector for similarity search (`gemini-embedding-001`) |

## Full schema

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `creation_date` | TIMESTAMP | NULLABLE | When the ticket was created |
| `title` | STRING | NULLABLE | Ticket subject or title |
| `content` | STRING | NULLABLE | Full ticket body text |
| `status` | STRING | NULLABLE | Ticket status (e.g. solved, closed, open) |
| `solved_at` | TIMESTAMP | NULLABLE | When the ticket was resolved |
| `star_rating` | STRING | NULLABLE | User-provided star rating for the support interaction |
| `product` | STRING | NULLABLE | Firefox product the ticket relates to |
| `locale` | STRING | NULLABLE | Ticket language/locale |
| `group_name` | STRING | NULLABLE | Support group that handled the ticket |
| `via_channel` | STRING | NULLABLE | Channel through which the ticket was submitted |
| `automation_category` | INTEGER | NULLABLE | Automation-assigned category tag |
| `type` | STRING | NULLABLE | Ticket type |
| `summary_generated` | STRING | NULLABLE | LLM-generated summary |
| `category_generated` | STRING | NULLABLE | LLM-generated category |
| `language_generated` | STRING | NULLABLE | LLM-detected language |
| `entities_generated` | STRING | REPEATED | LLM-extracted entities |
| `topics_generated` | STRING | REPEATED | LLM-generated topic tags |
| `sentiment_score` | FLOAT | NULLABLE | Sentiment score -1 to 1 |
| `recency_score` | FLOAT | NULLABLE | Recency weight for ranking |
| `metadata` | RECORD | NULLABLE | Additional metadata fields |
| `embedding` | FLOAT | REPEATED | Vector for similarity search (`gemini-embedding-001`) |

## Embedding model

All embeddings use `gemini-embedding-001` via Vertex AI. The orchestrator embeds the user's question with the same model at query time — dimensionality must match.

## How VECTOR_SEARCH is used

```sql
SELECT base.title, base.summary_generated, base.category_generated,
       base.sentiment_score, base.product, base.star_rating, base.recency_score,
       distance, 'zendesk' AS _source
FROM VECTOR_SEARCH(
    TABLE `<project>.customer_experience_derived.zendesk_retrieval_index`,
    'embedding',
    (SELECT <query_embedding> AS embedding),
    top_k => 5,
    distance_type => 'COSINE'
)
[WHERE base.creation_date >= '...' AND ...]
ORDER BY distance ASC
```

Lower `distance` = more semantically similar to the question.

## Interpreting Zendesk results

- **Use for:** Understanding what bugs or problems users are reporting, ticket volume by category, product-specific issue patterns.
- **Do not use for:** Sentiment analysis — `sentiment_score` here does not reliably reflect user sentiment. Use Kitsune `sentiment_score` instead.
- **`star_rating`** reflects user satisfaction with the support interaction, not with the Firefox product itself.
