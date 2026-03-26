---
name: glean-description-lookup
description: Use this skill when looking up field descriptions for Mozilla Glean telemetry tables (tables ending in _live or _stable, e.g. firefox_desktop_stable.newtab_v1). Fetches descriptions from the Glean Dictionary (dictionary.telemetry.mozilla.org) using WebFetch with targeted field extraction — only the fields referenced in query.sql, never the full table schema. Works with metadata-manager and schema-enricher skills.
---

# Glean Description Lookup

**Composable:** Works with metadata-manager (for applying descriptions to schema.yaml) and schema-enricher (for enriching derived table schemas)
**When to use:** A source table ends in `_live` or `_stable` and you need field descriptions for schema.yaml generation or enrichment

## ⚠️ Scope — Only for `_live` and `_stable` Tables

This skill applies **only** to:
- Tables ending in `_live` (e.g. `firefox_desktop_live.events_v1`)
- Tables ending in `_stable` (e.g. `firefox_desktop_stable.newtab_v1`)

These tables are NOT in the `/sql` directory. They are live Glean ingestion tables managed outside bigquery-etl.

For all other tables (`_derived`, `_bi`, `mozdata`, etc.) — read `schema.yaml` from the local `/sql` directory instead.

## Workflow

### Step 1: Confirm table is `_live` or `_stable`

Check the source table referenced in `query.sql`:

```bash
grep -E "FROM|JOIN" query.sql | grep -oE "[a-z_]+\.(.*_live|.*_stable)\.[a-z_]+"
```

If no `_live` or `_stable` table is found → **do not use this skill**. Use the local `/sql` directory.

### Step 2: Extract fields used from that table in `query.sql`

Read `query.sql` and identify every field selected or filtered from the `_live`/`_stable` source. List them explicitly before fetching anything.

```bash
# Helper: extract all field references
python scripts/extract_query_fields.py query.sql
```

Record:
```
Source table: firefox_desktop_stable.newtab_v1
Fields used: [submission_timestamp, client_info.client_id, metrics.string.newtab_locale, ...]
```

### Step 3: Map the BigQuery table name to a Glean Dictionary URL

Use READ `references/app_id_map.md` for the full mapping. The general pattern:

```
BigQuery dataset:  firefox_desktop_stable  or  firefox_desktop_live
BigQuery table:    newtab_v1

Glean app_id:      firefox_desktop
Glean table:       newtab

URL:  https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/newtab
```

**Derivation rule (when app_id not in the map):**
1. Strip `_live` or `_stable` suffix from the BigQuery dataset → that is the `app_id`
2. Strip the `_v<N>` suffix from the BigQuery table name → that is the Glean table name

### Step 4: Check table size before fetching

```
WebFetch:
URL: <glean_url>
Prompt: "How many top-level fields does this table have? Give me just a count."
```

Decision:
- < 20 fields → safe to request full schema
- 20–50 fields → request by section (e.g. `event.*`, `metrics.*`, `client_info.*`)
- > 50 fields → request **only the specific fields from Step 2**

### Step 5: Fetch descriptions with targeted WebFetch

Use a targeted prompt listing only the fields from Step 2. Never request the full schema for large tables.

**Template prompt:**
```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table>
Prompt: "Extract the name, BigQuery type, mode (NULLABLE/REPEATED), and description for
these fields only: <comma-separated list from Step 2>. Return as a list."
```

**Example:**
```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/newtab
Prompt: "Extract the name, type, mode, and description for these fields only:
submission_timestamp, client_info.client_id, metrics.string.newtab_locale,
ping_info.seq. Return as a simple list."
```

### Step 6: Map Glean types to BigQuery types

Use this mapping when writing descriptions to `schema.yaml`:

| Glean type | BigQuery type | Notes |
|---|---|---|
| string | STRING | |
| quantity / counter | INTEGER | |
| boolean | BOOLEAN | |
| datetime / date | TIMESTAMP / DATE | Check Glean probe definition |
| labeled_counter | RECORD | Nested key/value |
| event (extras) | RECORD | Nested |
| url | STRING | |
| uuid | STRING | |
| ARRAY of X | (X type) + mode: REPEATED | |

### Step 7: Return structured results

Return a lookup table for use by metadata-manager or schema-enricher:

```
| field                          | glean_type | bq_type   | mode     | description |
|-------------------------------|------------|-----------|----------|-------------|
| submission_timestamp           | datetime   | TIMESTAMP | NULLABLE | The time at which the ping was submitted to the ingestion endpoint. |
| client_info.client_id          | uuid       | STRING    | NULLABLE | A UUID identifying the client. |
| metrics.string.newtab_locale   | string     | STRING    | NULLABLE | The locale of the Firefox newtab page as reported by the client. |
```

## Token Efficiency Rules

| Table size | Strategy |
|---|---|
| < 20 fields | Request full schema |
| 20–50 fields | Request by category (e.g., all `client_info.*` fields) |
| > 50 fields | Request only the specific fields from Step 2 |

**Never** use a generic prompt like "give me the full schema" for events or metrics tables — these can be 200+ fields and 10k+ tokens.

## Error Handling

| Problem | Action |
|---|---|
| 404 from Glean Dictionary | Table may be too new or use a non-standard app_id. Try alternate app_id variations (see `references/app_id_map.md`). |
| Field not found in response | Field may be nested under a RECORD parent. Re-request the parent category. |
| Table not in Glean Dictionary | Fall back to `./bqetl query schema update` to generate schema structure, then infer descriptions from field name and product context. |
| `_stable` table has different schema than `_live` | Use the `_stable` URL — stable tables reflect the validated ping schema. |

## Integration with Other Skills

| Skill | When to invoke |
|---|---|
| `metadata-manager` | Pass lookup results to populate `schema.yaml` descriptions for the derived table |
| `schema-enricher` | Use results to fill `schema.yaml` for a derived table built from a `_live`/`_stable` source |
| `column-description-finder` | Use instead of this skill for derived/aggregated fields that come from base schemas (`global.yaml`, `app_<name>.yaml`) |

## Quick Reference

**Glean Dictionary base URL:**
```
https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table_name>
```

**Common app_id mappings** — see `references/app_id_map.md` for the full list.

**Script:**
```bash
# Extract all field references from a query
python scripts/extract_query_fields.py path/to/query.sql
```
