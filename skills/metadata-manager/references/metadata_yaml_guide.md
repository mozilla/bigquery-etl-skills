# Metadata.yaml Reference Guide

## Purpose

Metadata files define table ownership, scheduling, partitioning, and BigQuery configuration.

## Required Fields

```yaml
friendly_name: Human-Readable Table Name
description: >
  Multi-line description of the table's purpose.
  Use > for folded multi-line (joins lines with spaces).
  Use |- for literal multi-line (preserves line breaks).
owners:
  - email@mozilla.com
  - another@mozilla.com
```

## Common Labels

```yaml
labels:
  application: firefox          # Product/application name
  schedule: daily               # Update frequency (daily, hourly, weekly)
  table_type: client_level      # Data granularity (client_level, aggregated)
  dag: bqetl_main_summary      # Airflow DAG name
  owner1: username             # Primary owner username (without @mozilla.com)
```

**Common application values:**
- `firefox` - Firefox Desktop
- `fenix` - Firefox for Android
- `firefox_ios` - Firefox for iOS
- `relay` - Firefox Relay
- `mozilla_vpn` - Mozilla VPN
- `pocket` - Pocket

**Common schedule values:**
- `daily` - Updates once per day
- `hourly` - Updates every hour
- `weekly` - Updates once per week
- `monthly` - Updates once per month

## Scheduling Configuration

**Common scheduling patterns:**

```yaml
scheduling:
  dag_name: bqetl_main_summary           # Airflow DAG to run this query
  date_partition_parameter: submission_date  # For incremental queries; null for full refresh
  date_partition_offset: -7              # Optional: delay processing by N days
  start_date: '2021-01-19'              # Optional: when query scheduling began
  priority: 85                           # Optional: Airflow task priority
```

**Key scheduling options:**
- `date_partition_parameter: submission_date` - For incremental queries (most common)
- `date_partition_parameter: null` - For full table refresh queries
- `depends_on_past`, `parameters`, `depends_on`, `depends_on_tables_existing` - See scheduling reference

**For detailed scheduling options:** https://mozilla.github.io/bigquery-etl/reference/scheduling/

## BigQuery Configuration

**Time Partitioning:**

```yaml
bigquery:
  time_partitioning:
    type: day                          # or hour
    field: submission_date             # partition field name
    require_partition_filter: true     # require WHERE clause on partition
    expiration_days: 775              # optional: auto-delete old partitions (≈2 years)
```

**Partitioning strategies:**
- **Day partitioning** (most common): Use `type: day` with `field: submission_date`
- **Hour partitioning**: Use `type: hour` with `field: submission_timestamp` for hourly granularity
- **Partition filter requirement**: Set `require_partition_filter: true` for large tables to enforce partition filtering
- **Expiration**: Set `expiration_days: 775` (~2 years + buffer) for client-level data, adjust based on retention requirements

**Clustering:**

```yaml
bigquery:
  clustering:
    fields:
      - sample_id     # first clustering field (most selective)
      - client_id     # additional clustering fields
      - country       # up to 4 total fields
```

**Common clustering patterns:**
- Client-level: `[sample_id, client_id]`
- Event-level: `[event_category, sample_id, client_id]`
- Time-series: `[submission_date, sample_id]`

**Clustering best practices:**
- Order by query pattern frequency (most filtered/joined first)
- Max 4 clustering fields
- Choose fields that are frequently used in WHERE clauses or JOIN conditions

## Dependencies

Reference upstream tables/views:

```yaml
references:
  view.sql:
    - moz-fx-data-shared-prod.telemetry_derived.clients_daily_v6
    - moz-fx-data-shared-prod.telemetry.main
```

This helps with:
- Dependency tracking in Airflow
- Impact analysis for schema changes
- Documentation of data lineage

## Incremental Query Settings

For tables that process one partition at a time:

```yaml
scheduling:
  date_partition_parameter: submission_date  # Must match query parameter
bigquery:
  time_partitioning:
    field: submission_date                   # Must match output column
```

**Requirements:**
- Query must accept `@submission_date` parameter
- Query must output `submission_date` column
- Use `WRITE_TRUNCATE` disposition to replace partition

## Data Retention

**Partition expiration:**
```yaml
bigquery:
  time_partitioning:
    expiration_days: 775  # ~2 years for client-level data
```

**Common retention periods:**
- Client-level telemetry: 775 days (~2 years + buffer)
- Aggregated data: No expiration (or much longer)
- Temporary/staging: 30-90 days
- Compliance-sensitive: Follow data governance policies

## Legacy Tables

For tables without descriptions:

```yaml
metadata:
  require_column_descriptions: false  # Only for legacy tables
```

**Note:** All new tables should include descriptions. Only use this for maintaining existing tables.

## Best Practices

1. **Ownership:**
   - List at least 2 owners for redundancy
   - Use team email lists when appropriate
   - Keep owner list current

2. **Descriptions:**
   - Explain what the table is for
   - Mention key use cases
   - Note any important caveats or limitations
   - Reference related tables or documentation

3. **Labels:**
   - Be consistent with existing tables
   - Include `table_type` for client-level data
   - Use `owner1` for primary contact

4. **Scheduling:**
   - Set appropriate `date_partition_offset` for data latency
   - Use correct DAG for the data domain
   - Consider downstream dependencies

## Reference Examples

**Simple metadata:**
- `sql/moz-fx-data-shared-prod/mozilla_vpn_derived/users_v1/metadata.yaml`

**Partitioned & clustered:**
- `sql/moz-fx-data-shared-prod/telemetry_derived/clients_daily_event_v1/metadata.yaml`

**Key structure:**
```yaml
friendly_name: Human-Readable Table Name
description: Multi-line description
owners: [email@mozilla.com]
labels: {application: firefox, schedule: daily, table_type: client_level}
scheduling: {dag_name: bqetl_main_summary, date_partition_parameter: submission_date}
bigquery:
  time_partitioning: {type: day, field: submission_date, expiration_days: 775}
  clustering: {fields: [sample_id, client_id]}
```
