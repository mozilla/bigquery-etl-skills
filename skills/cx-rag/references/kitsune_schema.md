# kitsune_retrieval_index Schema Reference

**Table:** `<project>.customer_experience_derived.kitsune_retrieval_index`
**Purpose:** Semantic search index over SUMO forum content, pre-embedded for vector similarity queries.

## Columns used by the orchestrator

| Column | BigQuery Type | Description |
|--------|--------------|-------------|
| `title` | STRING | Original post/question title written by the user |
| `content` | STRING | Full raw text of the post or question |
| `answer_content` | STRING | Accepted or top answer content |
| `summary_generated` | STRING | LLM-generated summary of the post |
| `category_generated` | STRING | LLM-generated high-level category |
| `sentiment_score` | FLOAT | User sentiment: -1.0 (very negative) to 1.0 (very positive) |
| `recency_score` | FLOAT | Recency weight for ranking |
| `product` | STRING | Firefox product the post relates to |
| `topic` | STRING | Topic classification from SUMO |

## All columns

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `creation_date` | DATE | NULLABLE | When the post was created |
| `title` | STRING | NULLABLE | Post title |
| `content` | STRING | NULLABLE | Full post content |
| `product` | STRING | NULLABLE | Firefox product |
| `locale` | STRING | NULLABLE | Post language/locale |
| `topic` | STRING | NULLABLE | SUMO topic classification |
| `tier1_topic` | STRING | NULLABLE | Top-level topic tier |
| `tier2_topic` | STRING | NULLABLE | Mid-level topic tier |
| `tier3_topic` | STRING | NULLABLE | Leaf-level topic tier |
| `answer_content` | STRING | NULLABLE | Top answer text |
| `type` | STRING | NULLABLE | Post type |
| `forum_post_creator_self_answer` | BOOLEAN | NULLABLE | Whether OP answered their own question |
| `num_helpful_votes` | INTEGER | NULLABLE | Helpful vote count |
| `num_unhelpful_votes` | INTEGER | NULLABLE | Unhelpful vote count |
| `summary_generated` | STRING | NULLABLE | LLM-generated summary |
| `category_generated` | STRING | NULLABLE | LLM-generated category |
| `language_generated` | STRING | NULLABLE | LLM-detected language |
| `entities_generated` | STRING | REPEATED | LLM-extracted entities |
| `topics_generated` | STRING | REPEATED | LLM-generated topic tags |
| `sentiment_score` | FLOAT | NULLABLE | Sentiment score -1 to 1 |
| `recency_score` | FLOAT | NULLABLE | Recency weight for ranking |
| `embedding` | FLOAT | REPEATED | Vector for similarity search (`gemini-embedding-001`) |
| `metadata` | RECORD | NULLABLE | Additional metadata fields |

## Embedding model

All embeddings use `gemini-embedding-001` via Vertex AI. The orchestrator embeds the user's question with the same model at query time — dimensionality must match.

## How VECTOR_SEARCH is used

```sql
SELECT base.<content_cols>, distance
FROM VECTOR_SEARCH(
    TABLE `<project>.customer_experience_derived.kitsune_retrieval_index`,
    'embedding',
    (SELECT <query_embedding> AS embedding),
    top_k => 5,
    distance_type => 'COSINE'
)
ORDER BY distance ASC
```

Lower `distance` = more semantically similar to the question.
