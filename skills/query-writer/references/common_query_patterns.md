# Common Query Patterns

## Event Processing with Bit Patterns

Track activity over time using bit patterns:

```sql
-- Track if user was active today
CAST(active_hours_sum > 0 AS INT64) AS days_active_bits,

-- Track URI visits with thresholds
CAST(uri_count >= 5 AS INT64) AS days_visited_5_uri_bits,
```

## Active Users Calculation

```sql
-- Standard active user definition
COALESCE(
  scalar_parent_browser_engagement_total_uri_count_normal_and_private_mode_sum,
  scalar_parent_browser_engagement_total_uri_count_sum
) > 0
```

## Standard JOINs

**Always join on both partition and clustering fields:**

See `assets/join_example.sql` for complete example.

## UNNEST for Repeated Fields

See `assets/unnest_example.sql` for complete example.

## Performance Best Practices

**Key optimization techniques:**
- Filter on partition columns: `WHERE submission_date = @submission_date`
- Avoid `SELECT *` - list only needed columns
- Filter data before JOINs to reduce shuffling
- Use `sample_id` for testing (e.g., `WHERE sample_id = 0` for 1% sample)
- Use approximate functions when exact counts not needed (e.g., `approx_count_distinct()`)

**For detailed optimization guidance:** https://docs.telemetry.mozilla.org/cookbooks/bigquery/optimization.html
