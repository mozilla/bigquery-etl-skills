# SQL Formatting Conventions

## Basic Formatting

- Use uppercase for SQL keywords: `SELECT`, `FROM`, `WHERE`, `GROUP BY`, etc.
- Use 2-space indentation
- Place each field on its own line in SELECT statements
- Align major clauses at the same indentation level

## Table References

**Always fully qualify table references:**

```sql
FROM
  `moz-fx-data-shared-prod.telemetry.events`
```

## UDF References

```sql
-- Using mozfun UDFs
mozfun.map.get_key(map_field, 'key_name')
mozfun.norm.truncate_version(app_version, 'major')

-- Full project qualification
`moz-fx-data-shared-prod.udf.function_name`()
```

## Header Comments

Include clear documentation:

```sql
-- Daily per-client aggregation of event counts
-- See https://bugzilla.mozilla.org/show_bug.cgi?id=123456
-- Excludes test clients (sample_id = 99)
SELECT
  ...
```

**What to include:**
- Brief explanation of query purpose
- Bug/ticket references
- Any data filtering or exclusions
- Business context if relevant

## CTE Naming Conventions

**When to use CTEs:**
- Complex queries that benefit from breaking logic into steps
- Improving readability over nested subqueries
- Reusing intermediate results

**CTE naming:**
- Use descriptive names: `base`, `filtered_events`, `daily_aggregates`, `final`
- Common pattern: `base` for initial data selection
- Avoid generic names like `temp1`, `temp2`
