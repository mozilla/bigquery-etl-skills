---
name: column-description-finder
description: Use this skill when looking up, auditing, or managing column descriptions from global, application-specific, and dataset-specific column definition YAML files (bigquery_etl/schema/global.yaml, bigquery_etl/schema/app_<name>.yaml, and bigquery_etl/schema/<dataset>.yaml). Use it to find a description for a specific column, list all columns in a base schema, audit which columns in a table's schema.yaml are covered by base schemas, or identify columns missing descriptions. Works with schema-enricher skill.
---

# Column Description Finder

**Composable:** Invoked by schema-enricher (Step 0c) and base-schema-audit (Step 3) for base schema coverage audits
**When to use:** Finding column descriptions, auditing base schema coverage, listing available columns in global/app/dataset schemas

## Overview

Mozilla bigquery-etl maintains base schema YAML files that define standard column
descriptions for fields used across many tables:

- **`bigquery_etl/schema/global.yaml`** — common telemetry fields, read live from: https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/global.yaml
- **`bigquery_etl/schema/app_<name>.yaml`** — application-specific fields (e.g., `app_newtab.yaml`), read live from: `https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/app_<name>.yaml`
- **`bigquery_etl/schema/<dataset>.yaml`** — dataset-specific fields, read live from: `https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/<dataset_name>.yaml`

This skill helps:
1. **Find** a column's description, type, and aliases in base schemas
2. **List** all columns defined in a base schema file
3. **Audit** a table's schema.yaml to see which columns are covered by base schemas
4. **Identify** columns missing descriptions in a table

## 🚨 REQUIRED - Read These Files on Every Invocation

**ALWAYS fetch and read the live YAML files before answering — never rely on cached or assumed field data.**

1. **App-specific schema** (read first — highest priority):
   - `https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/app_<name>.yaml`
   - Check `bigquery_etl/schema/` for available app schema files (`app_*.yaml` pattern).
   - Use WebFetch to retrieve the file; if it returns 404, no app schema exists for that application.

2. **Dataset-specific schema** (read second):
   - `https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/<dataset_name>.yaml`
   - Check `bigquery_etl/schema/` for available dataset schema files.
   - Use WebFetch to retrieve the file; if it returns 404, no dataset schema exists for that dataset.

3. **Global schema** (read third — fallback):
   - https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/global.yaml

4. **Format and conventions:** READ `references/column_definition_yaml_guide.md`

## Quick Start

### Find a Column's Description

```bash
# Search global.yaml for a column
python scripts/find_column_description.py submission_date

# Search global.yaml + app_newtab.yaml (named file + global)
python scripts/find_column_description.py pocket_clicks --dataset app_newtab

# Search global.yaml + ads_derived.yaml (named file + global)
python scripts/find_column_description.py clicks --dataset ads_derived

# Search all available base schemas (app-specific first, then dataset-specific, then global)
python scripts/find_column_description.py my_column --all-datasets
```

**Output shows:** name, source file, type, mode, aliases, description

### List All Columns in a Base Schema

```bash
# List global.yaml columns
python scripts/find_column_description.py --list-all

# List ads_derived.yaml columns
python scripts/find_column_description.py --list-all --dataset ads_derived

# List all available base schema files
python scripts/audit_base_schema_coverage.py --list-schemas
```

### Audit a Table's Base Schema Coverage

```bash
# Check which columns in a table have base schema descriptions available.
# If metadata.yaml contains app_schema: <name>, that app schema is auto-applied.
python scripts/audit_base_schema_coverage.py telemetry_derived.clients_daily_v1

# Override or explicitly specify an app-specific schema (takes priority over metadata.yaml)
python scripts/audit_base_schema_coverage.py telemetry_derived.newtab_daily_interactions_aggregates_v1 --app-schema app_newtab

# Check coverage including dataset-specific schema
python scripts/audit_base_schema_coverage.py ads_derived.impressions_v1 --dataset-schema

# Check coverage including both app-specific and dataset-specific schemas
python scripts/audit_base_schema_coverage.py telemetry_derived.newtab_daily_interactions_aggregates_v1 --app-schema app_newtab --dataset-schema

# Show only columns missing descriptions
python scripts/audit_base_schema_coverage.py ads_derived.impressions_v1 --missing-only --dataset-schema
```

**Output shows:**
- Columns covered by base schemas (and which file)
- Columns with custom descriptions (defined in schema.yaml but not in any base schema)
- Columns with no description at all

> **Note:** Only top-level columns are matched against base schemas. Nested RECORD fields are not included in coverage analysis.

## Common Workflows

### Workflow 1: Looking Up a Column Description

When a user asks "what does the `country` column mean?" or "what is `dau`?":

1. Run `find_column_description.py <column_name>`
2. If not found, try `--all-datasets` to search all schemas
3. Report the description and source
4. If still not found, note the column is not in any base schema

### Workflow 2: Before Creating a Schema

When creating schema.yaml for a new derived table:

1. Run `audit_base_schema_coverage.py <dataset>.<table>` after initial schema generation
   - Add `--app-schema <app_name>` if the table belongs to an app (or set `app_schema` in `metadata.yaml`)
   - Add `--dataset-schema` if the dataset has a matching `<dataset_name>.yaml`
2. Review which columns are covered by base schemas
3. Apply base schema descriptions directly from the audit output
4. For uncovered columns, use the `schema-enricher` skill to fill descriptions from upstream schemas, query context, or application context

### Workflow 3: Identify Missing Descriptions

When checking metadata completeness for a table:

1. Run `audit_base_schema_coverage.py <dataset>.<table> --missing-only`
2. Show the user which columns have no description
3. For columns in base schemas → recommend applying base schema
4. For custom columns → generate descriptions based on field name and context

### Workflow 4: Adding New Column Definitions to Base Schemas

When a column is used in multiple derived tables and needs a standard description:

1. Determine if it belongs in global.yaml (used everywhere), an app-specific yaml (app_<name>.yaml, cross-dataset for a specific app), or a dataset-specific yaml (<dataset>.yaml)
   - For auditing an entire dataset or table prefix to classify many columns at once, use the `base-schema-audit` skill instead of doing this manually
2. READ `assets/example_global_entries.yaml` to see the correct format
3. Add the entry with name, type, mode, description, and aliases
4. Verify description quality using the checklist in `references/column_definition_yaml_guide.md`

## Script Reference

### `find_column_description.py`

Searches base schemas for a column by name or alias.

```
Usage: python scripts/find_column_description.py <column_name> [options]

Options:
  --dataset DATASET      Named base schema file to search (in addition to global.yaml), e.g., ads_derived or app_newtab
  --all-datasets         Search all available schemas (app-specific first, then dataset-specific, then global)
  --list-all             List all columns in the selected schema(s)
  --base-schemas-dir     Path to bigquery_etl/schema/ (default: bigquery_etl/schema)
```

### `audit_base_schema_coverage.py`

Audits a table's schema.yaml against base schemas.

```
Usage: python scripts/audit_base_schema_coverage.py <dataset>.<table> [options]

Options:
  --app-schema APP_SCHEMA  App-specific schema to check first (e.g., app_newtab)
  --dataset-schema         Include dataset-specific schema (inferred from dataset name)
  --missing-only           Show only columns with no description
  --list-schemas           List all available base schema files
  --sql-dir                Path to sql/ directory (default: sql)
  --base-schemas-dir       Path to bigquery_etl/schema/ (default: bigquery_etl/schema)
```

## Key Files

| File | Purpose |
|------|---------|
| https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/global.yaml | Live global schema — READ on every invocation |
| `https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/app_<name>.yaml` | Live app-specific schema — READ when an app schema applies; 404 means none exists |
| `https://raw.githubusercontent.com/mozilla/bigquery-etl/main/bigquery_etl/schema/<dataset>.yaml` | Live dataset schema — READ when dataset has a matching file |
| `references/column_definition_yaml_guide.md` | YAML structure, alias matching, priority order, conventions |
| `assets/example_global_entries.yaml` | Format-only template for adding new column definitions |
