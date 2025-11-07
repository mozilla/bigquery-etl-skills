-- User-level aggregation pattern
-- Example of standard user aggregation with metrics
WITH base AS (
  SELECT
    submission_date,
    client_id,
    sample_id,
    normalized_channel,
    country,
  FROM
    `moz-fx-data-shared-prod.telemetry.clients_daily`
  WHERE
    submission_date = @submission_date
)
SELECT
  submission_date,
  client_id,
  sample_id,
  COUNT(*) AS n_events,
  SUM(metric_value) AS total_metric,
  MAX(last_seen) AS last_activity,
FROM
  base
GROUP BY
  submission_date,
  client_id,
  sample_id
