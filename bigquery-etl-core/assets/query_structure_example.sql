-- Example BigQuery ETL Query Structure
-- This template shows the standard structure for a query.sql file
-- Header comment explaining query purpose
-- References: Bug/Ticket numbers, Related queries
-- Author: Team name
-- Date: Creation date
-- Main query using standard patterns
SELECT
  -- Standard partition field (required for most tables)
  submission_date,
  -- Standard Mozilla identifiers
  client_id,
  sample_id,
  -- Additional dimensions
  normalized_channel,
  normalized_country_code,
  app_version,
  -- Metrics (prefix counts with n_)
  COUNT(*) AS n_events,
  COUNT(DISTINCT session_id) AS n_sessions,
  -- Aggregations or transformations
  SUM(duration) AS total_duration_seconds
FROM
  -- Source table with appropriate partitioning
  `moz-fx-data-shared-prod.{dataset}.{table_name}`
WHERE
  -- Partition filter (required for incremental queries)
  submission_date = @submission_date
  -- Additional filters
  AND normalized_channel IN ('release', 'beta', 'nightly')
GROUP BY
  submission_date,
  client_id,
  sample_id,
  normalized_channel,
  normalized_country_code,
  app_version
