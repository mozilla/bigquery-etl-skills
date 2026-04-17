# Zendesk Overview

## What is Zendesk?

Zendesk is a customer support ticket management platform used by Mozilla to track issues and bugs reported by Firefox users. When users contact Mozilla Support directly (e.g. via a help form), their requests are routed into Zendesk as tickets.

Unlike SUMO forum posts, Zendesk tickets are structured support interactions — they are not publicly visible and represent direct user-to-support-staff communication.

## What the data represents

The `zendesk_retrieval_index` table contains processed and embedded Zendesk ticket content. This means:

- **Audience:** Firefox users who actively reached out for help — typically experiencing a specific problem.
- **Signal type:** Structured problem reports. Stronger signal for bug identification than for general sentiment.
- **Coverage:** Desktop and mobile Firefox, Firefox for Android, Firefox for iOS, and other Mozilla products.
- **Language:** Varies by locale; filter with `--locale` for language-specific analysis.

## Key differences from Kitsune

| Dimension | Kitsune (SUMO) | Zendesk |
|-----------|---------------|---------|
| Visibility | Public forum | Private support tickets |
| Content | Questions + community answers | Direct user-to-staff reports |
| Best use | Sentiment analysis, topic discovery | Bug identification, problem frequency |
| Sentiment | `sentiment_score` is reliable | `sentiment_score` is unreliable — do not use for sentiment |
| Volume | Higher (public forum) | Lower (direct contact) |

## Known limitations

| Limitation | Impact |
|-----------|--------|
| Not real-time | Index is periodically refreshed; very recent tickets may not be included |
| Sentiment is unreliable | `sentiment_score` is LLM-generated from ticket text and does not reliably reflect how the user feels |
| Skewed toward severe problems | Users who file tickets are more likely to have serious, unresolved issues |
| `star_rating` scope | Reflects satisfaction with the support interaction, not with Firefox itself |

## Interpreting results

Use Zendesk results to answer questions like:
- What bugs or errors are users reporting most frequently?
- What product areas generate the most support tickets?
- Are there specific error messages or failure modes appearing across tickets?

Do **not** use Zendesk for:
- Measuring user sentiment (use Kitsune instead)
- Understanding general user opinion or feature feedback
