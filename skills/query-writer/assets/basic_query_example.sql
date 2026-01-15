-- Daily per-client aggregation of event counts
-- Example of basic SQL formatting and structure
SELECT
  submission_date,
  sample_id,
  client_id,
  COUNT(*) AS n_total_events,
  COUNTIF(event_category = 'example') AS n_example_events,
FROM
  `moz-fx-data-shared-prod.telemetry.events`
WHERE
  submission_date = @submission_date
GROUP BY
  submission_date,
  sample_id,
  client_id
