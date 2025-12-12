# Glean Dictionary Usage Patterns

## Overview

The Glean Dictionary contains schema information for live and stable telemetry tables. This guide explains how to efficiently extract field information from Glean Dictionary web pages using WebFetch when building or modifying BigQuery tables.

## When to Use Glean Dictionary

**Use Glean Dictionary for:**
- Tables ending in `_live` or `_stable`
- Tables in datasets like: `firefox_desktop_live`, `fenix_stable`, `org_mozilla_firefox_live`, etc.
- Tables that are NOT in the `/sql` directory (they're live ingestion tables, not derived)

**DO NOT use for:**
- Derived tables (use `/sql` directory instead)
- Tables with `_derived` in the dataset name

## Glean Dictionary Access

**Web URL:** https://dictionary.telemetry.mozilla.org/

**URL structure:**
```
https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table_name>

Examples:
- https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
- https://dictionary.telemetry.mozilla.org/apps/fenix/tables/metrics
- https://dictionary.telemetry.mozilla.org/apps/focus_android/tables/baseline
```

## Token Efficiency WARNING

⚠️ **CRITICAL: Glean Dictionary pages can be VERY large**

- Some tables have **hundreds of columns** (events, metrics, client_info, etc.)
- Fetching entire table schemas can consume **10,000+ tokens**
- **NEVER request full schemas for large tables**
- **ALWAYS use targeted WebFetch prompts**

## Efficient Extraction Strategies

### Strategy 1: Request Specific Fields (RECOMMENDED)

When you know which fields you need (from analyzing the query):

**Step 1: Identify needed fields from query**
```bash
# Extract specific fields from query
grep -oE '[a-z_]+\.[a-z_]+' query.sql | sort -u
```

**Step 2: Use WebFetch with targeted prompt**
```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
Prompt: "Extract the name, type, mode, and description for these fields only: event.name, event.timestamp, event.category"
```

### Strategy 2: Request Field Counts First

Before fetching fields, determine if the table is large:

```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/<app>/tables/<table>
Prompt: "How many fields does this table have? Just give me the count."
```

**Decision tree:**
- If < 20 fields: Safe to request full schema
- If 20-50 fields: Request in sections or specific fields only
- If > 50 fields: ONLY request specific fields you need

### Strategy 3: Request by Field Categories

For tables with many fields, request by category:

```
WebFetch:
Prompt: "Extract only the event.* fields from this table (name, type, description)"
```

## Finding Glean Dictionary Tables

### Method 1: Direct URL (if you know app and table)

```
URL Pattern: https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table_name>

Examples:
- firefox_desktop events: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
- fenix baseline: https://dictionary.telemetry.mozilla.org/apps/fenix/tables/baseline
- focus_android metrics: https://dictionary.telemetry.mozilla.org/apps/focus_android/tables/metrics
```

### Method 2: Search the Glean Dictionary

```
1. Visit: https://dictionary.telemetry.mozilla.org/
2. Use the search bar to find your app or table name
3. Browse to the specific table
4. Copy the URL for WebFetch
```

### Method 3: Infer from BigQuery Table Name

```
BigQuery table pattern: <app>_<ping>_<version>
Example: firefox_desktop_live.events_v1

Glean Dictionary URL:
- App: firefox_desktop
- Table: events
- URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
```

## Common Table Patterns

### Events Tables

**Name pattern:** `*_events_v1`, `events_v1`, `events_stream_v1`

**Typical structure:**
- `event` (RECORD) - Main event structure
  - `name` - Event name
  - `timestamp` - Event timestamp
  - `category` - Event category
  - `extra` (RECORD) - Event-specific extras
- `client_info` (RECORD) - Client metadata
- `metadata` (RECORD) - Submission metadata
- `metrics` (RECORD) - Associated metrics

**Token risk:** ⚠️ HIGH - Events tables often have 100+ fields

**Strategy:** Extract only `event.*` fields you need, skip metrics unless used

### Metrics Tables

**Name pattern:** `*_metrics_v1`, `baseline_v1`, `metrics_v1`

**Typical structure:**
- `metrics` (RECORD) - All metrics organized by type
  - `counter` (RECORD) - Counter metrics
  - `string` (RECORD) - String metrics
  - `boolean` (RECORD) - Boolean metrics
  - etc.
- `client_info` (RECORD) - Client metadata
- `ping_info` (RECORD) - Ping metadata

**Token risk:** ⚠️ VERY HIGH - Can have 200+ metric fields

**Strategy:** Extract only specific metrics used in query

### Baseline/Session Tables

**Name pattern:** `baseline_v1`, `session_v1`

**Typical structure:**
- Standard Glean ping fields
- Client info
- Metrics (smaller subset than metrics tables)

**Token risk:** ⚠️ MEDIUM - Usually 30-60 fields

**Strategy:** Can read full file if needed, or extract specific sections

## Field Extraction Examples

### Example 1: Extract Single Field with Description

```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
Prompt: "Extract the complete definition for the field event.name including type, mode, and description"
```

**Expected response format:**
```
event.name
- Type: STRING
- Mode: NULLABLE
- Description: The name of the event as defined in Glean...
```

### Example 2: Extract Multiple Related Fields

```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
Prompt: "Extract all event.* fields with their types and descriptions"
```

### Example 3: Extract Nested Fields (Metrics)

```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/metrics
Prompt: "Extract the metrics.counter fields with their types and descriptions"
```

## Mapping Glean Dictionary to schema.yaml

### Field Type Mapping

Glean Dictionary types → BigQuery types:

| Glean Type | BigQuery Type | Mode |
|-----------|--------------|------|
| STRING | STRING | NULLABLE |
| INTEGER | INTEGER | NULLABLE |
| BOOLEAN | BOOLEAN | NULLABLE |
| DATETIME | TIMESTAMP | NULLABLE |
| RECORD | RECORD | NULLABLE |
| ARRAY | (parent type) | REPEATED |

### Nested Field Handling

Glean uses dot notation: `event.name`, `metrics.counter.value`

In schema.yaml:
```yaml
fields:
- name: event
  type: RECORD
  mode: NULLABLE
  fields:
  - name: name
    type: STRING
    mode: NULLABLE
    description: "Description from Glean Dictionary"
```

## Description Quality in Glean Dictionary

**Quality level:** ⭐⭐⭐⭐⭐ HIGH

Glean Dictionary descriptions are generally **excellent** because they come from probe definitions written by engineers.

**When to use as-is:**
- Descriptions are specific and technical
- Includes data type, format, and meaning
- Explains metric calculation or event trigger

**When to improve:**
- Add context about how field is used in derived table
- Clarify transformations or aggregations applied
- Add business context not in technical description

## Example Workflow: Schema from Events Table

**Scenario:** Creating schema for derived table that queries `firefox_desktop_live.events_v1`

**Step 1: Identify fields from query**
```bash
# From query.sql:
# SELECT event.name, event.category, event.timestamp
# We need: event.name, event.category, event.timestamp
```

**Step 2: Construct Glean Dictionary URL**
```
BigQuery table: firefox_desktop_live.events_v1
App: firefox_desktop
Table: events
URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
```

**Step 3: Use WebFetch to extract only needed fields**
```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
Prompt: "Extract the name, type, mode, and description for these three fields only: event.name, event.category, event.timestamp"
```

**Step 4: Review extracted field information**
```
This returns only ~200-300 tokens instead of potentially thousands for the full table schema
```

**Step 5: Generate schema.yaml**
```yaml
fields:
- name: event_name
  type: STRING
  mode: NULLABLE
  description: "Event name from Glean events. <description from Glean Dictionary>"

- name: event_category
  type: STRING
  mode: NULLABLE
  description: "Event category from Glean events. <description from Glean Dictionary>"

- name: event_timestamp
  type: TIMESTAMP
  mode: NULLABLE
  description: "Event timestamp from Glean events. <description from Glean Dictionary>"
```

## Token Usage Comparison

**❌ BAD: Requesting full table schema**
```
WebFetch:
Prompt: "Give me the complete schema for the events table with all fields"
Token usage: ~8,000-12,000 tokens
Time: Slow, may hit limits
```

**✅ GOOD: Targeted field extraction**
```
WebFetch:
Prompt: "Extract name, type, and description for these fields only: event.name, event.category, event.timestamp"
Token usage: ~200-400 tokens
Time: Fast, efficient
```

**Savings:** 95%+ fewer tokens! 🎉

## Best Practices Summary

### DO:
- ✅ Check field count before requesting schema
- ✅ Use targeted WebFetch prompts for specific fields
- ✅ Request full schema only for small tables (< 20 fields)
- ✅ Use Glean descriptions as base (they're high quality)
- ✅ Construct URLs from BigQuery table names

### DON'T:
- ❌ Request full schema for large tables (> 50 fields)
- ❌ Fetch all fields when you only need a few
- ❌ Use DataHub for Glean table schemas (use Glean Dictionary directly)
- ❌ Ignore token usage warnings
- ❌ Use generic prompts like "show me everything"

## Troubleshooting

### Table Not Found

**Problem:** Can't find table in Glean Dictionary

**Solutions:**
1. Check if table is actually a live/stable table
2. Try different app_id variations (underscores vs hyphens)
   - Example: `org_mozilla_fenix` vs `fenix`
3. Search the Glean Dictionary website directly for the app name
4. Table might be too new - may not be in Glean Dictionary yet
5. Check if it's actually a derived table (use `/sql` directory instead)

### Field Not Found

**Problem:** WebFetch doesn't return expected field

**Solutions:**
1. Check field name spelling (case-sensitive)
2. Field might be nested: request parent category (e.g., "event" not "event.name")
3. Use broader prompt: "List all fields related to [category]"
4. Field might be in different section (metrics vs events vs client_info)
5. Browse the Glean Dictionary page manually to verify field exists

### Description Too Technical

**Problem:** Glean description is very technical

**Solutions:**
1. Use technical description as base
2. Add business context in derived schema
3. Simplify for end-user documentation
4. Keep technical detail, add "In this table:" prefix for context

## Additional Resources

- **Glean Dictionary Web:** https://dictionary.telemetry.mozilla.org/
- **Glean Documentation:** https://mozilla.github.io/glean/book/
- **Probe Scraper:** https://probeinfo.telemetry.mozilla.org/
