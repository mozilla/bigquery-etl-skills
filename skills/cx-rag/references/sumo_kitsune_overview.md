# SUMO and Kitsune Overview

## What is SUMO?

**SUMO** (support.mozilla.org) is Mozilla's primary user-facing support platform. It hosts:
- User forum posts and questions
- Knowledge Base (KB) articles written by Mozilla contributors
- Community answers to user questions

SUMO is the main channel where Firefox users report problems, ask for help, and share feedback about their experience with Mozilla products.

## What is Kitsune?

**Kitsune** is the open-source Django web application that powers SUMO. The name "kitsune" is used interchangeably with SUMO in the data layer — when you see `kitsune` in table names, it refers to data sourced from the SUMO platform.

GitHub: https://github.com/mozilla/kitsune

## What the data represents

The `kitsune_retrieval_index` table contains content from SUMO forum posts — questions and replies from real Firefox users. This means:

- **Language:** Predominantly English, but SUMO is multilingual. Non-English posts may be present.
- **Audience:** Firefox end-users of all technical levels, not developers.
- **Signal type:** Organic user feedback — unfiltered, sometimes emotional, often specific to a version or OS.
- **Coverage:** Desktop and mobile Firefox, Firefox for Android, Firefox for iOS, and occasionally other Mozilla products.

## Known limitations

| Limitation | Impact |
|-----------|--------|
| Not real-time | The index is periodically refreshed; very recent posts may not be included |
| Sentiment is LLM-generated | `sentiment_score` reflects the model's read of the content, not a human label |
| Categories/topics are LLM-generated | May occasionally misclassify edge-case posts |
| Skewed toward problems | Users tend to post when something is wrong, so the index over-represents negative experiences |
| English-dominant | Non-English content is present but may retrieve less reliably for non-English questions |

## Interpreting sentiment scores

The `sentiment_score` field ranges from -1 to 1:
- **-1.0 to -0.3**: Clearly negative — user is frustrated or reporting a breaking problem
- **-0.3 to 0.3**: Neutral — informational, mixed, or ambiguous
- **0.3 to 1.0**: Positive — user is happy, praising a feature, or reporting resolution

Because SUMO skews toward problem reports, average sentiment across the table will naturally be below 0. Low sentiment in retrieved results doesn't necessarily mean sentiment has gotten worse — compare against a baseline if trends matter.
