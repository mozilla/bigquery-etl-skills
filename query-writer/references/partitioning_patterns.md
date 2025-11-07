# Partitioning Patterns

## Incremental Queries (Most Common)

Always use partition filters:

```sql
WHERE
  submission_date = @submission_date
```

**Requirements:**
- Must accept `@submission_date` parameter
- Must output a `submission_date` column matching the parameter
- Use `WRITE_TRUNCATE` mode to replace partitions atomically

## Full Refresh Queries

For snapshot tables or full table rewrites:
- No `@submission_date` parameter needed
- Set `date_partition_parameter: null` in metadata.yaml

## Backfill vs Incremental Logic

Use Jinja templating for initialization:

```sql
{% if is_init() %}
  -- Full historical backfill logic
  WHERE submission_date BETWEEN '2020-01-01' AND @submission_date
{% else %}
  -- Incremental logic for single partition
  WHERE submission_date = @submission_date
{% endif %}
```

## Hourly and Sub-Daily Queries

For queries that run more frequently than daily:
- Set `date_partition_parameter: null` in metadata.yaml
- Use explicit `destination_table` with partition decorator in metadata
- Query filters by date: `WHERE DATE(submission_timestamp) = @submission_date`

**Reference example:** `sql/moz-fx-data-shared-prod/telemetry_derived/newtab_interactions_hourly_v1/`

**See:** https://mozilla.github.io/bigquery-etl/reference/scheduling/ for detailed hourly scheduling configuration
