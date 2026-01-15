# Jinja Templating

Queries are interpreted as Jinja templates before execution.

## Common Jinja Patterns

```sql
-- Initialization vs incremental
{% if is_init() %}
  AND submission_date BETWEEN '2020-01-01' AND @submission_date
{% else %}
  AND submission_date = @submission_date
{% endif %}

-- Reference metric-hub metrics
{{ metrics.calculate() }}

-- Reference metric-hub data sources
{{ metrics.data_source() }}
```

## Key Functions

- `is_init()` - Returns true during initialization/backfill
- Regular scheduled runs use the `else` branch

## Date and Time Handling

**Converting timestamps to dates:**
```sql
DATE(submission_timestamp) AS submission_date
```

**Safe timestamp conversions:**
```sql
SAFE.TIMESTAMP_MILLIS(timestamp_field)
```

**Using date parameters:**
```sql
WHERE submission_date = @submission_date
```
