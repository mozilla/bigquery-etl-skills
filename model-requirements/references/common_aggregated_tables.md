# Common Aggregated Tables

## Overview

This guide maps raw `_live` and `_stable` tables to their optimized aggregated alternatives in `_derived` datasets.

**Why use aggregated tables?**
- **Performance:** Pre-aggregated data means faster queries and lower cost
- **Deduplication:** No duplicate pings or events
- **Pre-joined dimensions:** Common fields like client info, dates already joined
- **Optimization:** Proper partitioning, clustering, and indexing
- **Documentation:** Better documented with tests and clear ownership

## General Patterns

### Dataset Suffixes

- `*_live` - Raw ingestion tables, may contain duplicates, minimal processing
- `*_stable` - Deduplicated version of _live, but still event/ping level
- `*_derived` - Aggregated, optimized tables (USE THESE!)

### When _live/_stable is Necessary

Sometimes you DO need raw tables:
- Building a new derived table (source must be _live/_stable)
- Need event-level detail not available in aggregations
- Accessing very recent data (< 24 hours old)
- Working with brand new pings/metrics not yet aggregated

**If using _live/_stable tables:**
- Document the reason in requirements
- Consider building a derived table as part of the work
- Note performance and cost implications

## Firefox Desktop Telemetry

### Main Ping

**Raw tables:**
- `telemetry_live.main_v5`
- `telemetry_stable.main_v4`

**Use instead:**
- `telemetry_derived.clients_daily_v1` - **Most common choice**
  - Grain: One row per client per day
  - Pre-aggregated metrics (active hours, searches, crashes, etc.)
  - Includes normalized fields (os, country, channel)
  - Partitioned by submission_date
  - Use for: Daily aggregations, client-level analysis, retention/engagement

- `telemetry_derived.clients_last_seen_v1`
  - Grain: One row per client per day with 28-day history
  - Includes bit patterns for daily activity (days_seen_bits)
  - Use for: Retention analysis, cohort analysis, MAU/DAU calculations

- `telemetry_derived.main_summary_v4` (deprecated but still used)
  - Grain: One row per main ping (not aggregated)
  - Use for: Legacy queries, ping-level analysis
  - Consider migrating to clients_daily_v1 if possible

### Events Ping

**Raw tables:**
- `telemetry_live.events_v1`
- `telemetry_stable.events_v1`

**Use instead:**
- `telemetry_derived.events_daily_v1`
  - Grain: One row per client per event type per day
  - Aggregates event counts by category, method, object
  - Use for: Daily event analysis, feature usage tracking

- `telemetry_derived.event_events_v1`
  - Grain: One row per event (individual event records)
  - Normalized event structure with extras parsed
  - Use for: Event-level analysis, detailed user flows

### Baseline Ping

**Raw tables:**
- `firefox_desktop_live.baseline_v1`
- `firefox_desktop_stable.baseline_v1`

**Use instead:**
- `firefox_desktop_derived.baseline_clients_daily_v1`
  - Grain: One row per client per day
  - Aggregated baseline metrics
  - Use for: Daily client activity, engagement metrics

## Mobile Products (Fenix, iOS, Focus)

### Pattern: `{product}_stable` → `{product}_derived`

Replace `{product}` with:
- `org_mozilla_fenix` (Firefox for Android)
- `org_mozilla_firefox` (Firefox for iOS)
- `org_mozilla_focus` (Focus for Android)
- `org_mozilla_ios_firefox` (Firefox for iOS - newer)
- etc.

### Baseline Ping

**Raw tables:**
- `{product}_stable.baseline_v1`

**Use instead:**
- `{product}_derived.baseline_clients_daily_v1`
  - Grain: One row per client per day
  - Pre-aggregated baseline metrics
  - Use for: Daily active users, engagement, retention

### Metrics Ping

**Raw tables:**
- `{product}_stable.metrics_v1`

**Use instead:**
- `{product}_derived.metrics_clients_daily_v1`
  - Grain: One row per client per day
  - Aggregated metrics from metrics ping
  - Use for: Daily metrics analysis, feature usage

### Events

**Raw tables:**
- `{product}_stable.events_v1`

**Use instead:**
- `{product}_derived.events_daily_v1` (if exists)
  - Grain: One row per client per event type per day
  - Aggregated event counts
  - Use for: Daily event analysis

- Or query events directly from `events_stream_v1` tables:
  - `{product}_derived.events_stream_v1`
  - Individual event records with parsed extras

## Cross-Product Tables

### Unified Metrics

**For mobile + desktop combined analysis:**

- `telemetry_derived.clients_daily_v1` (desktop)
- `{product}_derived.baseline_clients_daily_v1` (mobile)

**Union these with UNION ALL** for cross-product analysis. All have similar structure:
- client_id (standardized)
- submission_date
- Common dimensions (country, channel, os)

### Search Data

**Raw tables:**
- Search data scattered across main, baseline, metrics pings

**Use instead:**
- `search_derived.search_clients_daily_v8`
  - Grain: One row per client per day
  - Aggregated search counts by engine, source (urlbar, searchbar, etc.)
  - Covers both desktop and mobile
  - Use for: Search analysis, SAP (search access point) reporting

- `search_derived.mobile_search_clients_daily_v1`
  - Grain: One row per client per day (mobile only)
  - Mobile-specific search metrics
  - Use for: Mobile search analysis

## External Data Sources

### Adjust (Install Attribution)

**Raw tables:**
- `adjust_live.installs_v1`
- `adjust_stable.installs_v1`

**Use instead:**
- `adjust_derived.installs_v1` (if exists, check with lineage)
  - May be aggregated daily
  - Pre-deduplicated
  - Use for: Install attribution, campaign tracking

### Revenue Data

**Tables:**
- `revenue_derived.*` tables (already optimized)
- Check DataHub for specific table availability

**Note:** Revenue tables are typically in private-bigquery-etl repo, may need special access

## How to Find Aggregated Alternatives

### Method 1: DataHub Lineage

Use the datahub_lineage.py script:

```bash
python .claude/skills/metadata-manager/scripts/datahub_lineage.py <table_name> --direction downstream
```

**Look for:**
- Tables in `*_derived` datasets
- Tables with "daily" or "aggregates" in name
- Tables with description mentioning aggregation

### Method 2: Search bigquery-etl Repository

```bash
# Find derived tables from a source
grep -r "FROM.*<table_name>" sql/*/

# Example: Find what uses main_v5
grep -r "FROM.*main_v5" sql/*/
```

### Method 3: DataHub Search

Use DataHub search to find downstream consumers:

```
mcp__datahub-cloud__search with filters:
- platform: bigquery
- Search for table name
- Check "Downstream" tab in UI
```

## Decision Tree

```
Are you querying _live or _stable table?
│
├─ YES → Is there a _derived alternative?
│        │
│        ├─ YES → Use the _derived table!
│        │        Examples: clients_daily_v1, events_daily_v1
│        │
│        └─ NO → Do you need event-level detail?
│                 │
│                 ├─ YES → Use _stable table (deduplicated)
│                 │        Document reason in requirements
│                 │
│                 └─ NO → Consider creating a _derived table
│                          as part of this work
│
└─ NO → Already using optimized table! ✓
```

## Common Questions

### Q: When should I use clients_daily vs clients_last_seen?

**Use clients_daily_v1 when:**
- Analyzing metrics for specific days
- Joining with other daily tables
- Building daily aggregations

**Use clients_last_seen_v1 when:**
- Calculating retention (28-day history)
- MAU/DAU calculations
- Need to know activity pattern over time

### Q: Should I use main_summary_v4 or clients_daily_v1?

**Always prefer clients_daily_v1** unless:
- You need ping-level detail (multiple pings per client per day)
- Working with legacy queries that use main_summary_v4
- The specific field you need isn't aggregated in clients_daily_v1

### Q: How do I combine desktop and mobile data?

**Use UNION ALL pattern:**

```sql
SELECT
  client_id,
  submission_date,
  'desktop' AS platform,
  -- common metrics
FROM telemetry_derived.clients_daily_v1
WHERE ...

UNION ALL

SELECT
  client_id,
  submission_date,
  'fenix' AS platform,
  -- common metrics
FROM org_mozilla_fenix_derived.baseline_clients_daily_v1
WHERE ...
```

### Q: What if the aggregated table doesn't have the field I need?

**Options:**
1. **Check if field is in another aggregated table** (events, metrics, etc.)
2. **Join the aggregated table with source table** for specific field
3. **Use the _stable table** and document performance considerations
4. **Request the field be added** to the aggregated table (file issue)

## Summary

**General rule:** Always prefer `*_derived` tables over `*_live` or `*_stable` tables.

**Most commonly used derived tables:**
- `telemetry_derived.clients_daily_v1` (desktop)
- `{product}_derived.baseline_clients_daily_v1` (mobile)
- `search_derived.search_clients_daily_v8` (search)
- `telemetry_derived.clients_last_seen_v1` (retention)

**When in doubt:**
1. Use datahub_lineage.py to find downstream tables
2. Check similar queries in bigquery-etl repo
3. Ask in #data-help Slack channel
