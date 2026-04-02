---
name: glean-description-lookup
description: Use this skill when looking up field descriptions for Mozilla Glean telemetry tables (tables ending in _live or _stable, e.g. <app>_stable.<ping>_v1). Fetches descriptions from the Glean Dictionary (dictionary.telemetry.mozilla.org) using WebFetch with targeted field extraction — only the fields referenced in query.sql, never the full table schema.
---

# Glean Description Lookup

**When to use:** A source table ends in `_live` or `_stable` and you need field descriptions for schema.yaml generation or enrichment

## ⚠️ Scope — Only for `_live` and `_stable` Tables

This skill applies **only** to:
- Tables ending in `_live` (e.g. `<app>_live.<ping>_v1`)
- Tables ending in `_stable` (e.g. `<app>_stable.<ping>_v1`)

These tables are NOT in the `/sql` directory. They are live Glean ingestion tables managed outside bigquery-etl.

For all other tables (`_derived`, `_bi`, `mozdata`, etc.) — read `schema.yaml` from the local `/sql` directory instead.

## Workflow

### Step 1: Confirm table is `_live` or `_stable`

Check the source table referenced in `query.sql`:

```bash
grep -Ei "FROM|JOIN" query.sql | grep -oiE "[a-zA-Z0-9_-]+\.(.*_(live|stable))\.[a-zA-Z0-9_]+"
```

⚠️ **Backtick limitation:** This grep only matches unquoted identifiers. Backtick-quoted references (e.g. `` `project`.`dataset_stable`.`table` ``) will not appear in the output. If the grep returns nothing, either scan the query visually for `_stable`/`_live` dataset names, or skip ahead to Step 2 — the helper script handles all backtick quoting styles automatically.

If no `_live` or `_stable` table is found → **do not use this skill**. Use the local `/sql` directory.

### Step 2: Extract fields used from that table in `query.sql`

Choose the right flag based on your query:

| Query structure | Flag to use | Why |
|---|---|---|
| One Glean source table | `--glean-only` | Filters output to only Glean source tables |
| Multiple source tables, want fields from all Glean tables | `--glean-only` | Same — filters out non-Glean source tables |
| Multiple source tables, want fields from one specific Glean table | `--table <app>_stable.<ping>_v1` | Shows URL and suggested prompt for that table only; field extraction still covers the full query |

Run the helper script and record its full output:

```bash
# Single Glean table or all Glean tables
python scripts/extract_query_fields.py query.sql --glean-only

# Specific Glean table (dataset.table format; project prefix is optional)
python scripts/extract_query_fields.py query.sql --table <app>_stable.<ping>_v1
```

Record:
```
Source table: <app>_stable.<ping>_v1
Fields used: [<field_1>, <field_2>, <field_3>, ...]
```

⚠️ **Alias limitation:** The script captures all dotted identifiers but cannot determine which ones are table or UNNEST alias references. After running the script, review the field list for two issues:
- **Remove** any entries whose first segment is a known alias (e.g. `e.submission_timestamp` where `e` aliases the `_stable` table, or `ev.name` where `ev` is an `UNNEST` alias) — these are false positives with the alias prefix intact.
- **Add** any Glean paths that were only accessed via alias in the query and therefore do not appear in the list. Use the full unaliased Glean path (e.g. `submission_timestamp`, `events[].name`).

To find aliases: search `query.sql` for `FROM <table> AS <alias>` and `CROSS JOIN UNNEST(...) AS <alias>` patterns, then compare those alias names against the first segment of each field in the output.

⚠️ **Field cap:** The script always extracts and prints the full field list. However, the SUGGESTED WebFetch PROMPT section is capped at `--max-fields` (default 25). If you see a truncation warning on stderr, either use the full FIELD REFERENCES list manually (after reviewing for alias false positives), or re-run with `--max-fields 50` (or higher) and then review the expanded list for aliases before using it.

⚠️ **Keyword filtering:** The script automatically excludes SQL keywords and function names (e.g. `select`, `extract`, `count`) from the field list to reduce false positives. If a field appears absent from the output, verify it is not being silently filtered as a keyword — check `query.sql` directly.

### Step 3: Map the BigQuery table name to a Glean Dictionary URL

**Derivation rule (works for most apps):**
1. Strip `_live` or `_stable` suffix from the BigQuery dataset name → this is the **app_id** (dictionary URL form, uses underscores): `<app_id>_stable` → `<app_id>`
2. Strip the `_v<N>` suffix from the BigQuery table name → this is the Glean table name: `<table>_v1` → `<table>`

```
BigQuery dataset:  <app_id>_stable  or  <app_id>_live
BigQuery table:    <table>_v1

app_id (dictionary URL form, underscores):  <app_id>
Glean table name:                           <table>

URL:  https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table>
```

Consult `references/app_id_map.md` for known app mappings and alternate app_id variations. If your app is not listed, the derivation rule above works for all apps. To verify directly, visit https://dictionary.telemetry.mozilla.org/ and search for the app name — the URL contains the correct app_id.

⚠️ **Hyphen vs underscore:** The Glean Dictionary URL uses underscores (`<app_id>`). The probeinfo API (`probeinfo.telemetry.mozilla.org`) requires hyphens (`<app-id>`). If using the probeinfo API as a fallback, replace `_` with `-` in the app_id.

### Step 4: Determine fetch strategy from table type

Derive the table type from your BigQuery table name (e.g. `baseline_v1` → `baseline`, `metrics_v1` → `metrics`). The table below gives guidance on what to expect — but the actual strategy decision is made in Step 5 based on how many fields you extracted in Step 2 (≤ 25 → targeted, > 25 → sectional).

| Table type | Typical field count | Strategy |
|---|---|---|
| `events` / `metrics` | 100–500+ | Targeted: request only fields from Step 2 |
| `crash` | 30–100 | Sectional or targeted |
| `baseline` | 30–60 | Sectional: request by category (e.g. `client_info.*`) |
| `newtab` | 20–80 | Targeted or sectional depending on field count |
| `first_session` | 10–30 | Usually safe to request full schema |
| `deletion_request` | < 10 | Safe to request full schema |

### Step 5: Fetch descriptions with targeted WebFetch

Use your cleaned field list from Step 2 (after alias review). Never copy the script's SUGGESTED WebFetch PROMPT directly — it uses the raw unreviewed field list and may include alias false positives.

**Choose your strategy by field count:**
- **≤ 25 fields** → use the targeted prompt (single request)
- **> 25 fields** → use the sectional prompt (one request per category: `client_info`, `metrics`, `ping_info`, etc.)

**Targeted prompt:**
```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table>
Prompt: "Extract the name, BigQuery type, mode (NULLABLE/REPEATED), and description for
these fields only: <comma-separated cleaned list from Step 2>. Return as a list with one entry per field."
```

**Sectional prompt** (for tables with 25+ fields — repeat per category):
```
WebFetch:
URL: https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table>
Prompt: "Extract the name, BigQuery type, mode (NULLABLE/REPEATED), and description for
all fields in the <category> section (e.g. client_info, ping_info, metrics). Return as a list with one entry per field."
```

Categories are the top-level field groupings shown on the Glean Dictionary table page (e.g. `client_info`, `ping_info`, `metadata`, `metrics`). Visit the dictionary URL directly to see the structure for your table and identify which categories to request. For `metrics` tables with many metric types, you can also request by sub-type (e.g. `metrics.string`, `metrics.counter`).

### Step 6: Map Glean types to BigQuery types

Use this mapping when writing descriptions to `schema.yaml`:

| Glean type | BigQuery type | Notes |
|---|---|---|
| `string` / `text` / `url` | STRING | |
| `quantity` / `counter` | INTEGER | |
| `boolean` | BOOLEAN | |
| `datetime` | TIMESTAMP | |
| `date` | DATE | |
| `uuid` / `jwe` | STRING | |
| `labeled_counter` / `labeled_boolean` / `labeled_string` | RECORD | Nested key/value pairs |
| `memory_distribution` / `timing_distribution` / `custom_distribution` | RECORD | Has `values`, `sum`, `count` subfields |
| `rate` | RECORD | Has `numerator`, `denominator` subfields |
| `object` | STRING | Serialized JSON |
| `event` (extras) | RECORD | Nested |
| `url_encoded` | STRING | |
| ARRAY of X | (X type) + mode: REPEATED | In schema.yaml: set `mode: REPEATED`; if X is a struct, set `type: RECORD` |

### Step 7: Return structured results

Produce a lookup table mapping each field to its type and description. This table is used to populate `schema.yaml` — the `schema_path` column shows where in the YAML nesting hierarchy each field lives, which is essential for correctly placing descriptions in nested RECORD fields.

```
| field                              | glean_type | bq_type   | mode     | schema_path                                              | description |
|-----------------------------------|------------|-----------|----------|----------------------------------------------------------|-------------|
| submission_timestamp               | datetime   | TIMESTAMP | NULLABLE | fields[submission_timestamp]                             | The time at which the ping was submitted to the ingestion endpoint. |
| client_info.client_id              | uuid       | STRING    | NULLABLE | fields[client_info] → fields[client_id]                  | A UUID identifying the client. |
| metrics.<type>.<metric_name>       | string     | STRING    | NULLABLE | fields[metrics] → fields[<type>] → fields[<metric_name>] | Description from Glean Dictionary. |
```

## Error Handling

| Problem | Action |
|---|---|
| 404 from Glean Dictionary | Try in order: (1) check alternate app_id variations in `references/app_id_map.md`; (2) visit https://dictionary.telemetry.mozilla.org/ and search for the app name to get the exact URL; (3) fall back to probeinfo API with hyphens: `https://probeinfo.telemetry.mozilla.org/glean/<hyphenated-app-id>/metrics`. |
| Field not found in response | Diagnose in order: (1) It may be nested under a RECORD parent — re-request the parent category (e.g. request `client_info` if `client_info.client_id` is missing). (2) It may be an alias false positive from Step 2 — verify the field exists in the Glean Dictionary at all. (3) The field name may use hyphens in the Dictionary (rare) — try replacing underscores with hyphens. (4) The field may not exist in this specific table type; check the dictionary or ask the data owner. |
| Table not in Glean Dictionary | Fall back to `./bqetl query schema update` to generate schema structure, then infer descriptions from field name and product context. As a secondary fallback, try `https://probeinfo.telemetry.mozilla.org/glean/<hyphenated-app-id>/metrics` — note this API uses **hyphens** in the app_id (e.g. `<app-id>`, not `<app_id>`). |
| `_stable` table has different schema than `_live` | Use the `_stable` URL — stable tables reflect the validated ping schema. |

## Quick Reference

**Glean Dictionary base URL:**
```
https://dictionary.telemetry.mozilla.org/apps/<app_id>/tables/<table_name>
```
*(app_id uses underscores — strip `_live`/`_stable` from dataset name; see `references/app_id_map.md` for known mappings)*

**Script:**
```bash
# Extract all Glean field references from a query
python scripts/extract_query_fields.py path/to/query.sql --glean-only

# Scope to a specific source table (useful when query joins multiple tables)
python scripts/extract_query_fields.py path/to/query.sql --table <app>_stable.<ping>_v1

# Increase field cap for the suggested WebFetch prompt (default: 25)
python scripts/extract_query_fields.py path/to/query.sql --glean-only --max-fields 50
```
