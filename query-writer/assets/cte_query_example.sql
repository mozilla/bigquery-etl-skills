-- Creates a flattened events dataset
-- Example of using CTEs for complex queries
WITH base AS (
  SELECT
    DATE(submission_timestamp) AS submission_date,
    client_id,
    normalized_channel,
    event_category,
    event_method,
  FROM
    `moz-fx-data-shared-prod.telemetry.event`
  WHERE
    DATE(submission_timestamp) = @submission_date
),
filtered AS (
  SELECT
    *
  FROM
    base
  WHERE
    event_category IS NOT NULL
)
SELECT
  *
FROM
  filtered
