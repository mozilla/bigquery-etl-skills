# Dataset Naming Conventions

## Dataset Naming Patterns

Dataset names indicate their purpose through suffixes:

### By Suffix

- `{name}_derived` - Processed/transformed data (most common for ETL outputs)
- `{name}_external` - External data sources synced into BigQuery
- `{name}_syndicate` - Syndicated/shared data
- `{name}` (no suffix) - Raw ping data or stable tables

### Common Dataset Prefixes by Product/Source

- `telemetry_*` - Firefox telemetry data (e.g., `telemetry_derived`, `telemetry_stable`)
- `accounts_*` - Firefox Accounts/FxA data
- `contextual_services_*` - Contextual services data
- `ads_*` - Advertising data
- Product-specific: `activity_stream`, `addons`, `default_browser_agent`, etc.
- External services: `braze_*`, `adjust_*`, `acoustic_*`, `apple_ads_*`, etc.

### Special Datasets

- `analysis` - Ad-hoc analysis tables
- `backfills_staging_derived` - Staging area for backfills
- `mozfun` - User-defined functions

**Reference:** See https://docs.telemetry.mozilla.org/datasets/ for detailed dataset documentation

## Table Versioning Patterns

Tables use version suffixes:
- `{table_name}_v1` - Initial version
- `{table_name}_v2` - Second version (breaking changes)
- Increment version when making breaking schema changes

### Directory Structure

- Always flat: `sql/{project}/{dataset}/{table_name}/`
- Never use subdirectories within table directories

## Incremental vs Full Refresh

### Incremental Queries
Process one partition at a time (most common)
- Use `@submission_date` parameter
- Set `date_partition_parameter: submission_date` in metadata.yaml

### Full Refresh Queries
Rewrite entire table on each run
- Set `date_partition_parameter: null` in metadata.yaml

See query-writer and metadata-manager skills for implementation details.
