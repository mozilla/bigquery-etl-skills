# Column Definition YAML Guide

## Overview

Mozilla bigquery-etl uses two tiers of base schema YAML files to define standard column
descriptions that can be auto-applied to derived tables. These live in `bigquery_etl/schema/`.

## File Locations

```
bigquery_etl/schema/
├── global.yaml              # Common telemetry fields used across all datasets
├── app_newtab.yaml          # Newtab application-specific fields (app_*.yaml pattern)
├── ads_derived.yaml         # Ads dataset-specific fields
├── <dataset_name>.yaml      # Other dataset-specific fields
└── ...
```

### Naming Conventions

| Pattern | Type | Example |
|---------|------|---------|
| `global.yaml` | Global — fields shared across all datasets | submission_date, client_id |
| `app_<name>.yaml` | App-specific — fields for a specific product/application | app_newtab.yaml |
| `<dataset_name>.yaml` | Dataset-specific — fields scoped to one dataset | ads_derived.yaml |

## YAML Structure

### Field Entry Format

```yaml
fields:
  - name: submission_date
    type: DATE
    mode: NULLABLE
    description: "Date when the data was submitted to the ingestion pipeline."
    aliases:
      - sub_date
      - date
```

### Supported Field Properties

| Property | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Canonical column name |
| `type` | Yes | BigQuery type (DATE, STRING, INTEGER, FLOAT, BOOLEAN, TIMESTAMP, RECORD) |
| `mode` | No | NULLABLE (default), REQUIRED, REPEATED |
| `description` | Yes | Human-readable description of the column |
| `aliases` | No | Alternative names that map to this canonical column |

### Nested Fields (RECORD type)

```yaml
fields:
  - name: experiments
    type: RECORD
    mode: REPEATED
    description: "Active experiments for this client."
    fields:
      - name: key
        type: STRING
        description: "Experiment slug identifier."
      - name: value
        type: RECORD
        fields:
          - name: branch
            type: STRING
            description: "Experiment branch name."
```

## Schema Tiers

### global.yaml

**Location in repo:** `bigquery_etl/schema/global.yaml`
**Raw URL:** https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/global.yaml

Contains fields that appear across many datasets and tables (submission_date, client_id, country, dau/wau/mau, normalized_channel, normalized_os, attribution_*, etc.).

**READ this file at the start of every invocation** to get the current field list, descriptions, types, modes, and aliases.

### App-Specific Schemas (e.g., app_newtab.yaml)

**Location in repo:** `bigquery_etl/schema/app_<name>.yaml`
**Raw URL pattern:** `https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/app_<name>.yaml`

Known app schema files (check `bigquery_etl/schema/` for the current list):
- `app_newtab.yaml` — https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/app_newtab.yaml

Contains fields specific to a product/application used across multiple datasets (e.g., newtab pocket/topsite/search interaction columns).

**READ the relevant app schema file** when working with tables from a known application. App schemas take priority over dataset schemas.

### Dataset-Specific Schemas (e.g., ads_derived.yaml)

**Location in repo:** `bigquery_etl/schema/<dataset_name>.yaml`
**Raw URL pattern:** `https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/<dataset_name>.yaml`

Known dataset schema files (check `bigquery_etl/schema/` for the current list):
- `ads_derived.yaml` — https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/ads_derived.yaml

Contains fields specific to one dataset (impressions, clicks, revenue, cpm, flight_id, campaign_id, partner_name, rate_type, etc.).

**READ the relevant dataset schema file** when the table's dataset has a matching `<dataset_name>.yaml`.

## How Alias Matching Works

When running `./bqetl query schema update --use-global-schema`, bqetl matches columns
by exact name first, then by aliases:

```yaml
# In global.yaml
- name: submission_date
  aliases:
    - sub_date
    - date
```

If your table has a column named `sub_date`, it matches `submission_date` via alias
and inherits the description. bqetl will recommend renaming `sub_date` to `submission_date`.

## Priority Order

Always check schemas in this order — higher priority wins:

```
App-specific schema (highest priority — e.g., app_newtab.yaml)
    ↓
Dataset schema (e.g., ads_derived.yaml)
    ↓
Global schema (fallback — global.yaml)
    ↓
No match → field needs manual description
```

If a column name exists in multiple schemas, the highest-priority schema description wins.

## How to Check Available Descriptions

```bash
# List all global columns
python scripts/find_column_description.py --list-all

# List all columns in a dataset schema
python scripts/find_column_description.py --list-all --dataset ads_derived

# Find a specific column's description
python scripts/find_column_description.py submission_date
python scripts/find_column_description.py clicks --dataset ads_derived

# Search all available schemas
python scripts/find_column_description.py my_column --all-datasets
```

## How to Audit a Table's Coverage

```bash
# See which columns have base schema descriptions available
python scripts/audit_base_schema_coverage.py telemetry_derived.clients_daily_v1

# Include dataset-specific schema
python scripts/audit_base_schema_coverage.py ads_derived.impressions_v1 --dataset-schema

# Show only missing descriptions
python scripts/audit_base_schema_coverage.py ads_derived.impressions_v1 --missing-only
```

## Metadata-Driven App Schema Detection

Tables can declare their app schema in `metadata.yaml` using the `app_schema` field:

```yaml
# metadata.yaml
friendly_name: Newtab Interactions Daily Aggregates
description: A daily aggregation of newtab interactions.
app_schema: app_newtab   # <-- declares which app_*.yaml applies to this table
owners:
- me@mozilla.com
```

When `app_schema` is set, `audit_base_schema_coverage.py` automatically uses it without requiring `--app-schema` on the command line:

```bash
# auto-detects app_schema from metadata.yaml
python scripts/audit_base_schema_coverage.py telemetry_derived.newtab_daily_interactions_aggregates_v1
# [metadata] Using app_schema 'app_newtab' from metadata.yaml
```

Passing `--app-schema` explicitly always overrides the metadata value.

## Adding New Columns to Base Schemas

When a column is used across multiple derived tables and has a stable definition,
consider adding it to the appropriate base schema:

1. **Identify the right file:**
   - Common across many datasets → `global.yaml`
   - Specific to one application (cross-dataset) → `bigquery_etl/schema/app_<name>.yaml`
   - Specific to one dataset → `bigquery_etl/schema/<dataset>.yaml`

2. **Add the entry following the format above**

3. **Include aliases** for common alternative names to maximize coverage

4. **Write a complete description** (see quality checklist below)

## Description Quality Checklist

- [ ] Clear meaning without needing to look up the field
- [ ] Units specified (seconds, bytes, USD, count)
- [ ] NULL handling described if relevant
- [ ] Scope clarified (per-client, per-day, lifetime)
- [ ] Calculation method noted if derived
- [ ] Source(s) mentioned if aggregated from multiple places
