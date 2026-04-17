# Knowledge Base Overview

## What is the Mozilla Knowledge Base?

The Mozilla Knowledge Base (KB) is a curated collection of help articles published on support.mozilla.org. Articles are written and maintained by Mozilla contributors and staff to answer common user questions and solve known problems. This is the same content that Mozilla Support agents reference when responding to forum posts and Zendesk tickets.

The KB is not user-generated content — it represents Mozilla's official guidance on Firefox features, known issues, and recommended solutions.

## What the data represents

The `knowledge_base_retrieval_index` table contains processed and embedded KB article content. This means:

- **Audience:** Written for Firefox end-users of all technical levels.
- **Signal type:** Official guidance — authoritative answers to known questions.
- **Coverage:** Desktop and mobile Firefox, Firefox for Android, Firefox for iOS, and other Mozilla products.
- **Language:** Multilingual; filter with `--locale` for language-specific articles.

## Key differences from Kitsune and Zendesk

| Dimension | Kitsune (SUMO) | Zendesk | Knowledge Base |
|-----------|---------------|---------|----------------|
| Source | User forum posts | Support tickets | Official Mozilla articles |
| Content | User questions + answers | Bug reports | How-to guides, known issues |
| Best use | Sentiment, user pain points | Bug identification | What official solutions exist |
| Sentiment | Reliable user signal | Unreliable | Not user sentiment — article tone only |
| Date filter | Yes | Yes | **No** — no `creation_date` column |
| Product filter | Yes | Yes | **No** — no `product` column |

## Known limitations

| Limitation | Impact |
|-----------|--------|
| No date column | Cannot be filtered by time period — always returns results from the full article corpus |
| No product column | Cannot be filtered by Firefox product |
| Sentiment is article tone | `sentiment_score` reflects the LLM's read of the article text, not how users feel |
| Curated, not exhaustive | Only covers topics that have been formally documented; emerging issues may not yet have articles |
| Not real-time | Index is periodically refreshed; very recently published articles may not be included |

## Interpreting results

Use Knowledge Base results to answer questions like:
- What official guidance exists for a given topic?
- Is there a known solution to this reported problem?
- What does Mozilla recommend users do about this issue?

Do **not** use Knowledge Base results for:
- Measuring user sentiment (use Kitsune instead)
- Understanding how widespread a problem is (use Kitsune or Zendesk instead)

## Using the slug field

Each article has a `slug` field that maps to its live URL:

```
https://support.mozilla.org/kb/<slug>
```

Always include this link when citing a KB article in an answer.
